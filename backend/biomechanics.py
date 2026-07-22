import numpy as np


def calculate_angle(a, b, c):
    """Angle at point b, formed by points a-b-c, in degrees."""
    a, b, c = np.array(a[:2]), np.array(b[:2]), np.array(c[:2])
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    angle = np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))
    return angle


def analyze_frame(keypoints: dict):
    """Computes joint angles + posture indicators for a single frame."""
    kp = keypoints

    knee_angle_left = calculate_angle(kp["left_hip"], kp["left_knee"], kp["left_ankle"])
    knee_angle_right = calculate_angle(kp["right_hip"], kp["right_knee"], kp["right_ankle"])
    elbow_angle_left = calculate_angle(kp["left_shoulder"], kp["left_elbow"], kp["left_wrist"])
    elbow_angle_right = calculate_angle(kp["right_shoulder"], kp["right_elbow"], kp["right_wrist"])
    hip_angle_left = calculate_angle(kp["left_shoulder"], kp["left_hip"], kp["left_knee"])
    hip_angle_right = calculate_angle(kp["right_shoulder"], kp["right_hip"], kp["right_knee"])

    # Trunk lean: angle of the shoulder-hip midline vs vertical
    shoulder_mid = np.mean([kp["left_shoulder"][:2], kp["right_shoulder"][:2]], axis=0)
    hip_mid = np.mean([kp["left_hip"][:2], kp["right_hip"][:2]], axis=0)
    trunk_vector = shoulder_mid - hip_mid
    trunk_lean = np.degrees(np.arctan2(trunk_vector[0], -trunk_vector[1] + 1e-8))

    # Knee valgus proxy: horizontal distance between knees vs between ankles
    knee_gap = abs(kp["left_knee"][0] - kp["right_knee"][0])
    ankle_gap = abs(kp["left_ankle"][0] - kp["right_ankle"][0]) + 1e-8
    knee_valgus_ratio = knee_gap / ankle_gap  # < 1 suggests knees caving inward

    return {
        "knee_angle_left": knee_angle_left,
        "knee_angle_right": knee_angle_right,
        "elbow_angle_left": elbow_angle_left,
        "elbow_angle_right": elbow_angle_right,
        "hip_angle_left": hip_angle_left,
        "hip_angle_right": hip_angle_right,
        "trunk_lean_degrees": trunk_lean,
        "knee_valgus_ratio": knee_valgus_ratio,
    }


def analyze_sequence(frames_data: list):
    """
    Runs analyze_frame across all frames, then aggregates into:
    - range of motion per joint
    - left/right symmetry scores
    - knee valgus risk flag
    - an overall movement quality score
    """
    per_frame_metrics = [analyze_frame(f["keypoints"]) for f in frames_data]

    if not per_frame_metrics:
        return {"error": "No pose data detected in video."}

    def series(key):
        return np.array([m[key] for m in per_frame_metrics])

    knee_l, knee_r = series("knee_angle_left"), series("knee_angle_right")
    hip_l, hip_r = series("hip_angle_left"), series("hip_angle_right")
    valgus = series("knee_valgus_ratio")
    trunk = series("trunk_lean_degrees")

    # Range of motion = max - min angle observed
    rom = {
        "knee_left": float(knee_l.max() - knee_l.min()),
        "knee_right": float(knee_r.max() - knee_r.min()),
        "hip_left": float(hip_l.max() - hip_l.min()),
        "hip_right": float(hip_r.max() - hip_r.min()),
    }

    # Symmetry: 100 = perfectly symmetric, drops as left/right diverge
    knee_symmetry = 100 - min(100, abs(knee_l.mean() - knee_r.mean()))
    hip_symmetry = 100 - min(100, abs(hip_l.mean() - hip_r.mean()))
    overall_symmetry = float(round((knee_symmetry + hip_symmetry) / 2, 1))

    # Knee valgus risk: ratio consistently < 0.8 flags inward knee collapse
    valgus_risk_frames = int((valgus < 0.8).sum())
    valgus_risk_pct = float(round(100 * valgus_risk_frames / len(valgus), 1))

    posture_stability = float(round(100 - min(100, float(np.std(trunk)) * 5), 1))

    # Simple weighted movement quality score (0-100)
    movement_quality_score = float(round(
        0.4 * overall_symmetry + 0.3 * posture_stability + 0.3 * (100 - valgus_risk_pct),
        1,
    ))

    if movement_quality_score >= 80:
        risk_category = "Low Risk"
    elif movement_quality_score >= 60:
        risk_category = "Moderate Risk"
    elif movement_quality_score >= 40:
        risk_category = "High Risk"
    else:
        risk_category = "Critical Risk"

    return {
        "frames_analyzed": len(per_frame_metrics),
        "range_of_motion": rom,
        "symmetry_score": overall_symmetry,
        "posture_stability_score": posture_stability,
        "knee_valgus_risk_pct": valgus_risk_pct,
        "movement_quality_score": movement_quality_score,
        "risk_category": risk_category,
    }