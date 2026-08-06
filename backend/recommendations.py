"""
Corrective Recommendation Engine (Milestone 3).

Turns the injury-risk and anomaly-detection output into concrete,
athlete-facing guidance grouped the way the spec's Athlete Dashboard
expects: exercises, mobility work, strengthening focus, recovery
planning, and training-load adjustments.
"""


def generate_recommendations(risk_result: dict, anomaly_result: dict) -> dict:
    exercises = []
    mobility = []
    strengthening = []
    recovery = []
    training_mods = []

    cat = risk_result["category_risks"]

    if cat.get("ACL Injury Risk", 0) >= 50:
        exercises.append("Single-leg landing drills with soft-knee cues")
        strengthening.append("Hip abductor and glute medius strengthening (band walks, clamshells)")
        mobility.append("Ankle dorsiflexion mobility work to reduce compensatory knee valgus")

    if cat.get("Hamstring Injury Risk", 0) >= 50:
        exercises.append("Nordic hamstring curls (eccentric-focused)")
        mobility.append("Dynamic hamstring/hip-flexor stretching before high-speed running")

    if cat.get("Ankle Sprain Risk", 0) >= 50:
        strengthening.append("Single-leg balance and proprioception drills")
        exercises.append("Resisted ankle inversion/eversion work")

    if cat.get("Shoulder Injury Risk", 0) >= 50:
        strengthening.append("Rotator cuff and scapular stabilizer strengthening")
        mobility.append("Thoracic spine and shoulder mobility routine")

    if cat.get("Lower Back Injury Risk", 0) >= 50:
        strengthening.append("Core and anti-rotation stability work (planks, Pallof press)")
        mobility.append("Hip flexor and thoracic extension mobility to reduce trunk lean")

    if cat.get("Overuse Injury Risk", 0) >= 50:
        recovery.append("Add a full rest or active-recovery day this week")
        training_mods.append("Reduce weekly training volume by 15-20% until fatigue markers normalize")

    if risk_result["movement_asymmetry_score"] >= 40:
        strengthening.append("Unilateral strength work to close the left/right imbalance")

    if anomaly_result.get("fatigue_trend") == "declining":
        recovery.append("Prioritize sleep and hydration; consider a deload week")
        training_mods.append("Lower training intensity until posture-stability scores recover")

    if anomaly_result.get("performance_decline_detected"):
        recovery.append("Flag for physiotherapist review — technique has dropped versus baseline")

    if risk_result["overall_risk_score"] >= 60:
        training_mods.append("Avoid high-impact/plyometric loading until the risk score drops below High")

    # Always give at least one item per bucket so the dashboard has something to show.
    if not exercises:
        exercises.append("Maintain current movement-prep routine — no elevated exercise flags")
    if not mobility:
        mobility.append("General mobility maintenance — no specific restrictions flagged")
    if not strengthening:
        strengthening.append("Continue balanced strength programming")
    if not recovery:
        recovery.append("Standard recovery protocol is sufficient")
    if not training_mods:
        training_mods.append("No training load changes recommended")

    return {
        "exercise_recommendations": exercises,
        "mobility_suggestions": mobility,
        "strengthening_recommendations": strengthening,
        "recovery_plan": recovery,
        "training_modifications": training_mods,
    }
