#!/usr/bin/env python3
"""
Reusable template: B2B Cold-Start Lead Scoring with TabICLv2.

When you have leads but zero labeled conversions, this script:
1. Loads real leads from a JSON file (adapt the loader for your schema)
2. Engineers features (adapt for your fields)
3. Generates synthetic conversion labels from industry-known patterns
4. Bootstrap-augments to reach sufficient training volume
5. Outputs a training CSV ready for TabICL

ADAPT: SECTOR_BASE_RATES, WEBSITE_IMPACT, CHANNEL_MULTIPLIER for your domain.
ADAPT: load_leads() and engineer_features() for your data schema.

Usage:
    python b2b_coldstart_lead_scorer.py --leads leads.json --output training.csv
"""

import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path


# ============================================================
# DOMAIN-SPECIFIC CONVERSION PATTERNS
# Adapt these for YOUR industry / geography
# ============================================================

# Base conversion rate by sector category
# Source: B2B digital marketing industry benchmarks for local businesses (FR-CH)
SECTOR_BASE_RATES = {
    "Restaurant":               0.025,   # High volume, saturated, low close rate
    "Salon de coiffure":        0.065,   # Image-driven, good prospects
    "Beauté":                   0.070,   # Similar to salon, slightly higher
    "Garage auto":              0.020,   # Not image-driven, low interest
    "Boulangerie / Pâtisserie": 0.015,   # Old school, very low
    "Immobilier":               0.055,   # High value, medium interest
    "Sport":                    0.045,   # Medium
    "Fleuriste":                0.035,   # Medium-low
    "Santé":                    0.010,   # Regulated, conservative, very low
    "Assurance":                0.050,   # Medium-high
    "Kiné / Ostéopathe":        0.015,   # Regulated
    "Cabinet comptable":        0.030,   # Conservative but business-minded
    "Avocat":                   0.025,   # Conservative
    "Plombier / Chauffagiste":  0.040,   # Practical, medium
}

# Multipliers: how each feature modifies base conversion probability
# No website = biggest opportunity (they NEED digital presence)
WEBSITE_IMPACT = {
    "none":          1.8,
    "has_website":   0.5,
    "facebook_only": 1.0,
}

CHANNEL_MULTIPLIER = {
    "instagram": 1.3,
    "email":     0.8,
    "sms":       1.1,
    "linkedin":  0.9,
}


# ============================================================
# ADAPTER: Load your leads (adapt for your schema)
# ============================================================

def load_leads(path: str) -> pd.DataFrame:
    """Load leads from JSON. Adapt the path format for your data source."""
    with open(path) as f:
        data = json.load(f)
    return pd.DataFrame(data)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract ML-ready numeric/categorical features from raw lead data.
    TabICL handles categorical (label-encoded) and numeric natively.
    Adapt field names for your schema.
    """
    features = pd.DataFrame()

    # Binary features
    features["has_website"] = (df["website_status"] == "has_website").astype(int)
    features["has_facebook_only"] = (df["website_status"] == "facebook_only").astype(int)
    features["no_website"] = (df["website_status"] == "none").astype(int)
    features["has_phone"] = (df["phone"].fillna("") != "").astype(int)
    features["has_opening_hours"] = (df["opening_hours"].fillna("") != "").astype(int)

    # Categorical (label encoded)
    features["sector_code"] = df["sector"].astype("category").cat.codes
    features["city_code"] = df["city"].astype("category").cat.codes
    features["channel_code"] = df["channel"].astype("category").cat.codes

    # Numeric
    features["current_score"] = df["score"].fillna(60).astype(float)
    features["name_length"] = df["name"].str.len().fillna(15).astype(float)
    features["lat"] = df["lat"].fillna(46.19).astype(float)
    features["lon"] = df["lon"].fillna(6.23).astype(float)

    return features


# ============================================================
# CORE: Synthetic label generation
# ============================================================

def generate_conversion_labels(df: pd.DataFrame, noise_level: float = 0.3):
    """Generate realistic conversion labels from industry-known patterns."""
    n = len(df)
    log_odds = np.zeros(n)

    for i in range(n):
        row = df.iloc[i]
        sector = row.get("sector", "Restaurant")
        ws = row.get("website_status", "none")
        channel = row.get("channel", "instagram")

        # Base rate for sector
        base = SECTOR_BASE_RATES.get(sector, 0.03)
        log_odds[i] = np.log(base / (1 - base))

        # Multipliers
        log_odds[i] += np.log(WEBSITE_IMPACT.get(ws, 1.0))
        log_odds[i] += np.log(CHANNEL_MULTIPLIER.get(channel, 1.0))

        # Binary signals
        if row.get("phone"):
            log_odds[i] += 0.14  # +15% reachable
        if row.get("opening_hours"):
            log_odds[i] += 0.10  # +10% established

        # Existing deterministic score (captures real signal)
        score = row.get("score", 60)
        log_odds[i] += (score - 60) * 0.015

    # Noise for realism
    log_odds += np.random.normal(0, noise_level, n)

    probs = 1 / (1 + np.exp(-log_odds))
    labels = (np.random.random(n) < probs).astype(int)
    return labels, probs


def generate_training_data(
    leads_path: str,
    n_augment: int = 3000,
    noise_level: float = 0.3,
    random_state: int = 42,
) -> pd.DataFrame:
    """Full pipeline: load → augment → engineer features → generate labels."""
    np.random.seed(random_state)

    real_df = load_leads(leads_path)
    print(f"Loaded {len(real_df)} real leads")

    # Bootstrap augmentation
    if n_augment > 0:
        augmented = real_df.sample(n=n_augment, replace=True, random_state=random_state)
        augmented = augmented.copy()
        augmented["score"] = (augmented["score"] + np.random.normal(0, 3, n_augment)).clip(0, 100)
        combined = pd.concat([real_df, augmented], ignore_index=True)
    else:
        combined = real_df.copy()

    print(f"Total after augmentation: {len(combined)}")

    features = engineer_features(combined)
    labels, probs = generate_conversion_labels(combined, noise_level)
    features["converted"] = labels

    print(f"Conversion rate: {labels.mean():.1%} ({labels.sum()}/{len(labels)})")
    return features


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--leads", required=True, help="Path to leads JSON")
    parser.add_argument("--output", default="training_data.csv")
    parser.add_argument("--n-augment", type=int, default=3000)
    parser.add_argument("--noise", type=float, default=0.3)
    args = parser.parse_args()

    df = generate_training_data(args.leads, args.n_augment, args.noise)
    df.to_csv(args.output, index=False)
    print(f"\n✅ Saved {len(df)} samples to {args.output}")


if __name__ == "__main__":
    main()
