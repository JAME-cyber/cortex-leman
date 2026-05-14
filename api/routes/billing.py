"""
Cortex Leman v5 — Stripe Billing Routes

Endpoints pour:
- Créer une session de checkout (abonnement récurrent)
- Recevoir les webhooks Stripe (paiement, annulation, etc.)
- Consulter le statut d'un abonnement client
- Gérer le cycle de vie des abonnements (upgrade/downgrade/cancel)
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends, Header
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

# ── Plan definitions ──

PLANS = {
    "sentinelle": {
        "name": "Sentinelle",
        "price_chf": 500,
        "price_id_env": "stripe_price_sentinelle",
        "features": [
            "Monitoring OWASP GenAI continu",
            "Alertes CVE sur stack IA",
            "Rapport conformité mensuel",
            "Certificat de conformité (valide tant qu'abonné)",
            "Dashboard read-only",
        ],
    },
    "garde": {
        "name": "Garde",
        "price_chf": 900,
        "price_id_env": "stripe_price_garde",
        "features": [
            "Tout Sentinelle +",
            "Re-audit trimestriel complet",
            "Mise à jour AIPD/DPIA",
            "Support DPO (questions illimitées)",
            "Revue nouveaux outils IA",
            "Veille réglementaire FR-CH",
        ],
    },
    "forteresse": {
        "name": "Forteresse",
        "price_chf": 1500,
        "price_id_env": "stripe_price_forteresse",
        "features": [
            "Tout Garde +",
            "Consulting stratégique IA (2h/mois)",
            "Hotline priorité (< 4h)",
            "Anticipation réglementaire",
            "Audit ad-hoc pour tout nouvel outil IA",
            "Co-pilotage DPO",
            "Rapport exécutif trimestriel board",
        ],
    },
}


# ── Models ──

class CheckoutRequest(BaseModel):
    client_id: str
    client_email: str
    plan: str  # sentinelle | garde | forteresse
    vertical: Optional[str] = None
    success_url: str = "https://cortexleman.ch/dashboard?session_id={CHECKOUT_SESSION_ID}"
    cancel_url: str = "https://cortexleman.ch/pricing?cancelled=true"


class SubscriptionStatus(BaseModel):
    client_id: str
    plan: str
    status: str  # active | past_due | canceled | trialing
    current_period_end: Optional[str] = None
    certificate_valid: bool = False


class WebhookEvent(BaseModel):
    type: str
    data: dict


# ── Endpoints ──

@router.get("/plans")
async def list_plans():
    """Liste les plans récurrents disponibles"""
    return {
        "plans": [
            {
                "id": plan_id,
                "name": plan["name"],
                "price_chf": plan["price_chf"],
                "price_id": getattr(settings, plan["price_id_env"], None),
                "features": plan["features"],
            }
            for plan_id, plan in PLANS.items()
        ]
    }


@router.post("/checkout")
async def create_checkout(req: CheckoutRequest):
    """
    Créer une session Stripe Checkout pour un abonnement récurrent.
    Redirige le client vers la page de paiement Stripe.
    """
    try:
        import stripe
    except ImportError:
        raise HTTPException(500, "stripe package not installed")

    if not settings.stripe_secret_key:
        raise HTTPException(500, "Stripe not configured (STRIPE_SECRET_KEY missing)")

    if req.plan not in PLANS:
        raise HTTPException(400, f"Invalid plan: {req.plan}. Must be one of: {list(PLANS.keys())}")

    price_id = getattr(settings, PLANS[req.plan]["price_id_env"])
    if not price_id:
        raise HTTPException(500, f"Price ID not configured for plan: {req.plan}")

    stripe.api_key = settings.stripe_secret_key

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            customer_email=req.client_email,
            line_items=[{"price": price_id, "quantity": 1}],
            metadata={
                "client_id": req.client_id,
                "plan": req.plan,
                "vertical": req.vertical or "",
            },
            success_url=req.success_url,
            cancel_url=req.cancel_url,
            subscription_data={
                "metadata": {
                    "client_id": req.client_id,
                    "plan": req.plan,
                    "vertical": req.vertical or "",
                }
            },
        )
        return {"checkout_url": session.url, "session_id": session.id}
    except stripe.error.StripeError as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(400, str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    """
    Webhook Stripe — traite les événements de paiement.
    Événements gérés:
    - checkout.session.completed → activer l'abonnement
    - customer.subscription.updated → mise à jour plan
    - customer.subscription.deleted → annulation
    - invoice.payment_failed → alerter
    """
    try:
        import stripe
    except ImportError:
        raise HTTPException(500, "stripe package not installed")

    if not settings.stripe_webhook_secret:
        raise HTTPException(500, "Stripe webhook secret not configured")

    payload = await request.body()
    stripe.api_key = settings.stripe_secret_key

    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")
    except Exception as e:
        raise HTTPException(400, f"Webhook error: {e}")

    event_type = event["type"]
    metadata = {}

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        client_id = metadata.get("client_id")
        plan = metadata.get("plan")
        logger.info(f"✅ Subscription activated: client={client_id} plan={plan}")
        # TODO: Activate subscription in DB
        # TODO: Generate initial certificate
        # TODO: Send welcome email

    elif event_type == "customer.subscription.updated":
        subscription = event["data"]["object"]
        metadata = subscription.get("metadata", {})
        client_id = metadata.get("client_id")
        plan = metadata.get("plan")
        logger.info(f"🔄 Subscription updated: client={client_id} plan={plan}")
        # TODO: Update subscription in DB
        # TODO: Update certificate if plan changed

    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        metadata = subscription.get("metadata", {})
        client_id = metadata.get("client_id")
        logger.info(f"❌ Subscription canceled: client={client_id}")
        # TODO: Mark subscription as canceled in DB
        # TODO: Revoke certificate
        # TODO: Send cancellation email

    elif event_type == "invoice.payment_failed":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        logger.warning(f"⚠️ Payment failed: customer={customer_id}")
        # TODO: Alert client + internal team
        # TODO: Grace period management

    else:
        logger.info(f"📨 Unhandled Stripe event: {event_type}")

    return {"received": True, "type": event_type}


@router.get("/subscription/{client_id}")
async def get_subscription_status(client_id: str):
    """Consulter le statut de l'abonnement d'un client"""
    try:
        import stripe
    except ImportError:
        raise HTTPException(500, "stripe package not installed")

    if not settings.stripe_secret_key:
        raise HTTPException(500, "Stripe not configured")

    stripe.api_key = settings.stripe_secret_key

    # Search for subscription by client_id metadata
    try:
        subscriptions = stripe.Subscription.search(
            query=f"metadata['client_id']:'{client_id}'",
            limit=1,
        )
        if not subscriptions.data:
            return SubscriptionStatus(
                client_id=client_id,
                plan="none",
                status="none",
            ).model_dump()

        sub = subscriptions.data[0]
        plan = sub.metadata.get("plan", "unknown")
        period_end = datetime.fromtimestamp(
            sub.current_period_end, tz=timezone.utc
        ).isoformat()

        return SubscriptionStatus(
            client_id=client_id,
            plan=plan,
            status=sub.status,
            current_period_end=period_end,
            certificate_valid=sub.status == "active",
        ).model_dump()

    except stripe.error.StripeError as e:
        logger.error(f"Stripe lookup error: {e}")
        raise HTTPException(400, str(e))


@router.post("/subscription/{client_id}/cancel")
async def cancel_subscription(client_id: str):
    """Annuler un abonnement (prend effet en fin de période)"""
    try:
        import stripe
    except ImportError:
        raise HTTPException(500, "stripe package not installed")

    if not settings.stripe_secret_key:
        raise HTTPException(500, "Stripe not configured")

    stripe.api_key = settings.stripe_secret_key

    try:
        subscriptions = stripe.Subscription.search(
            query=f"metadata['client_id']:'{client_id}'",
            limit=1,
        )
        if not subscriptions.data:
            raise HTTPException(404, f"No subscription found for client: {client_id}")

        sub = subscriptions.data[0]
        cancelled = stripe.Subscription.modify(
            sub.id,
            cancel_at_period_end=True,
        )
        return {
            "client_id": client_id,
            "status": "cancelling",
            "cancel_at": datetime.fromtimestamp(
                cancelled.cancel_at, tz=timezone.utc
            ).isoformat() if cancelled.cancel_at else None,
            "message": "Subscription will cancel at end of current period",
        }
    except stripe.error.StripeError as e:
        logger.error(f"Stripe cancel error: {e}")
        raise HTTPException(400, str(e))


@router.get("/health")
async def billing_health():
    """Vérifier si le module billing est configuré"""
    return {
        "stripe_configured": bool(settings.stripe_secret_key),
        "webhook_configured": bool(settings.stripe_webhook_secret),
        "plans": {
            plan_id: {
                "price_id": getattr(settings, plan["price_id_env"], None),
                "configured": bool(getattr(settings, plan["price_id_env"], None)),
            }
            for plan_id, plan in PLANS.items()
        },
    }
