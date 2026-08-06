"""
Movement Anomaly Detection Engine (Milestone 3).

Compares the biomechanics report for the video just analyzed against the
same athlete's own recent report history, rather than judging a single
video in isolation. Flags:
  - a technique deviation from the athlete's own baseline
  - a fatigue trend (posture stability drifting down over recent sessions)
  - a performance-decline flag for the recommendation/notification engines
"""

import numpy as np


def _clip(value, low=0.0, high=100.0):
    return max(low, min(high, value))


def detect_anomalies(current: dict, previous_reports: list) -> dict:
    """
    current: dict from biomechanics.analyze_sequence() for the video just analyzed
    previous_reports: models.BiomechanicalReport rows for this athlete's
                       earlier videos, ordered oldest -> newest
    """
    if not previous_reports:
        # No baseline yet — fall back to a light fatigue proxy from posture
        # instability alone, and skip the trend-based flags.
        return {
            "anomaly_detected": False,
            "technique_deviation_pct": 0.0,
            "fatigue_trend": "insufficient_data",
            "performance_decline_detected": False,
            "fatigue_score": round(_clip(0.3 * (100 - current["posture_stability_score"])), 1),
        }

    baseline_quality = float(np.mean([r.movement_quality_score for r in previous_reports]))
    quality_delta = current["movement_quality_score"] - baseline_quality
    technique_deviation_pct = round(abs(quality_delta), 1)

    # A meaningful drop from the athlete's own baseline flags an anomaly.
    anomaly_detected = quality_delta <= -10
    performance_decline_detected = quality_delta <= -15

    # Fatigue trend: posture stability across the last few sessions plus the
    # current one — a falling trend suggests accumulating fatigue.
    recent = [r.posture_stability_score for r in previous_reports[-3:]] + [
        current["posture_stability_score"]
    ]
    trend_slope = recent[-1] - recent[0] if len(recent) >= 2 else 0.0

    if trend_slope <= -8:
        fatigue_trend = "declining"
    elif trend_slope >= 8:
        fatigue_trend = "improving"
    else:
        fatigue_trend = "stable"

    fatigue_score = _clip(
        max(0.0, -trend_slope) * 3 + 0.2 * (100 - current["posture_stability_score"])
    )

    return {
        "anomaly_detected": bool(anomaly_detected),
        "technique_deviation_pct": technique_deviation_pct,
        "fatigue_trend": fatigue_trend,
        "performance_decline_detected": bool(performance_decline_detected),
        "fatigue_score": round(fatigue_score, 1),
    }
