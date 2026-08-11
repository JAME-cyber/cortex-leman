# Webhook Trigger Format — Scout LEC

## Endpoint
```
POST http://localhost:8644/webhooks/lec-scout
```

## Payload (JSON)
Le champ `event_type` est **obligatoire** — sans lui le POST est silencieusement ignoré (`{"status": "ignored", "event": "unknown"}`):
```json
{
  "event_type": "signal",
  "signal": "Texte du signal ou résumé à évaluer",
  "url": "https://source-optionnelle.com/article",
  "source": "digitimes | reuters | iea | manual"
}
```

## Signature HMAC (header obligatoire)
Header: `X-Webhook-Signature: <hex HMAC-SHA256 du body JSON brut>`

Le secret est celui retourné par `hermes webhook subscribe` (stocké dans `~/.hermes/webhook_subscriptions.json`).

## Script curl complet
```bash
SECRET="<secret-de-la-subscription>"
URL="http://localhost:8644/webhooks/lec-scout"
BODY='{"event_type":"signal","signal":"EU clears 659M EUR in subsidies for chip plants.","url":"https://example.com","source":"test"}'

SIG=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | awk '{print $NF}')

curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: $SIG" \
  -d "$BODY"
```

## Réponse attendue
- Succès: `{"status": "accepted", "route": "lec-scout", "event": "signal", "delivery_id": "..."}`
- Ignoré (event_type manquant): `{"status": "ignored", "event": "unknown"}`
- Signature invalide: `{"error": "Invalid signature"}` (HTTP 401)

## Après le POST
Le gateway lance une session agent dédiée qui:
1. Charge la skill `lec-scout`
2. Exécute le workflow (critères → collecte → jugement LLM → guardrails → verdict)
3. Délivre le verdict sur Telegram (chat configuré dans `--deliver-chat-id`)
