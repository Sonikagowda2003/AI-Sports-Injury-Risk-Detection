"""
Injury Risk Prediction Engine (Milestone 3).

Combines the per-video biomechanics report (Milestone 2) with athlete-level
context (injury history, training load) and a fatigue/anomaly signal into:
  - an overall weighted injury risk score (0-100, higher = riskier)
  - a risk category (Low / Moderate / High / Critical)
  - per-injury-category risk estimates (ACL, Hamstring, Ankle, Shoulder,
    Lower Back, Overuse)

Uses the weighted model from the project spec:

    Injury Risk Score =
        0.35 * Biomechanical Deviations
      + 0.20 * Historical Injury Factors
      + 0.20 * Movement Asymmetry
      + 0.15 * Training Load Indicators
      + 0.10 * Fatigue Indicators
"""

import numpy as np

INJURY_CATEGORIES = [
    "ACL Injury Risk",
    "Hamstring Injury Risk",
    "Ankle Sprain Risk",
    "Shoulder Injury Risk",
    "Lower Back Injury Risk",
    "Overuse Injury Risk",
]

# Keywords used to flag a category from the athlete's free-text injury history.
_CATEGORY_KEYWORDS = {
    "ACL Injury Risk": ["acl", "knee ligament", "knee reconstruction"],
    "Hamstring Injury Risk": ["hamstring"],
    "Ankle Sprain Risk": ["ankle"],
    "Shoulder Injury Risk": ["shoulder", "rotator cuff"],
    "Lower Back Injury Risk": ["back", "spine", "disc"],
    "Overuse Injury Risk": ["overuse", "tendinitis", "tendinopathy", "stress fracture"],
}

_TRAINING_LOAD_SCORES = {
    "very high": 95,
    "intense": 90,
    "heavy": 85,
    "high": 80,
    "moderate": 50,
    "medium": 50,
    "light": 20,
    "low": 20,
}


def _clip(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def score_historical_injury_factor(injury_history):
    """
    Returns (overall_score, per_category_score) derived from free-text
    injury history. No history -> 0 risk. Unrecognized text still counts
    as a moderate baseline, since *any* prior injury raises re-injury risk.
    """
    per_category = {cat: 0.0 for cat in INJURY_CATEGORIES}
    if not injury_history or not injury_history.strip():
        return 0.0, per_category

    text = injury_history.lower()
    matched = False
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            per_category[category] = 70.0
            matched = True

    if not matched:
        # History exists but doesn't name a tracked category — moderate baseline.
        for category in per_category:
            per_category[category] = 35.0

    overall = float(np.mean(list(per_category.values())))
    return overall, per_category


def score_training_load(training_load):
    """Maps a free-text training load field to a 0-100 risk indicator."""
    if not training_load or not training_load.strip():
        return 30.0  # unknown load — mild default risk
    text = training_load.lower()
    for key, score in _TRAINING_LOAD_SCORES.items():
        if key in text:
            return float(score)
    return 40.0  # text present but not recognized — mild-moderate default


def predict_injury_risk(biomech: dict, athlete, fatigue_score: float) -> dict:
    """
    biomech: dict returned by biomechanics.analyze_sequence()
    athlete: models.Athlete row (used for injury_history / training_load)
    fatigue_score: 0-100 output from anomaly_detection.detect_anomalies()
    """
    knee_valgus_risk_pct = biomech["knee_valgus_risk_pct"]
    posture_stability_score = biomech["posture_stability_score"]
    symmetry_score = biomech["symmetry_score"]
    upper_body_symmetry_score = biomech.get("upper_body_symmetry_score", symmetry_score)

    biomechanical_deviation_score = _clip(
        0.6 * knee_valgus_risk_pct + 0.4 * (100 - posture_stability_score)
    )
    movement_asymmetry_score = _clip(100 - symmetry_score)

    historical_overall, historical_per_category = score_historical_injury_factor(
        getattr(athlete, "injury_history", None)
    )
    training_load_score = score_training_load(getattr(athlete, "training_load", None))

    overall_risk_score = _clip(round(
        0.35 * biomechanical_deviation_score
        + 0.20 * historical_overall
        + 0.20 * movement_asymmetry_score
        + 0.15 * training_load_score
        + 0.10 * fatigue_score,
        1,
    ))

    if overall_risk_score < 20:
        risk_category = "Low Risk"
    elif overall_risk_score < 40:
        risk_category = "Moderate Risk"
    elif overall_risk_score < 60:
        risk_category = "High Risk"
    else:
        risk_category = "Critical Risk"

    # Per-category risk = category-specific biomechanical signal blended with
    # that category's historical-injury flag (30% weight).
    category_risks = {
        "ACL Injury Risk": _clip(
            0.7 * knee_valgus_risk_pct + 0.3 * movement_asymmetry_score
        ),
        "Hamstring Injury Risk": _clip(
            0.6 * movement_asymmetry_score + 0.4 * training_load_score
        ),
        "Ankle Sprain Risk": _clip(
            0.5 * knee_valgus_risk_pct + 0.5 * (100 - posture_stability_score)
        ),
        "Shoulder Injury Risk": _clip(100 - upper_body_symmetry_score),
        "Lower Back Injury Risk": _clip(100 - posture_stability_score),
        "Overuse Injury Risk": _clip(0.6 * training_load_score + 0.4 * fatigue_score),
    }
    for category, hist_score in historical_per_category.items():
        blended = 0.7 * category_risks[category] + 0.3 * hist_score
        category_risks[category] = round(_clip(blended), 1)

    return {
        "biomechanical_deviation_score": round(biomechanical_deviation_score, 1),
        "historical_injury_factor_score": round(historical_overall, 1),
        "movement_asymmetry_score": round(movement_asymmetry_score, 1),
        "training_load_score": round(training_load_score, 1),
        "fatigue_indicator_score": round(fatigue_score, 1),
        "overall_risk_score": overall_risk_score,
        "risk_category": risk_category,
        "category_risks": category_risks,
    }
