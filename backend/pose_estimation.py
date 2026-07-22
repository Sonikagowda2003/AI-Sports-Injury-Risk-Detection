import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose

# Maps MediaPipe's 33 landmarks to the "Key Body Points" your spec calls out
LANDMARK_MAP = {
    "left_shoulder": mp_pose.PoseLandmark.LEFT_SHOULDER,
    "right_shoulder": mp_pose.PoseLandmark.RIGHT_SHOULDER,
    "left_elbow": mp_pose.PoseLandmark.LEFT_ELBOW,
    "right_elbow": mp_pose.PoseLandmark.RIGHT_ELBOW,
    "left_wrist": mp_pose.PoseLandmark.LEFT_WRIST,
    "right_wrist": mp_pose.PoseLandmark.RIGHT_WRIST,
    "left_hip": mp_pose.PoseLandmark.LEFT_HIP,
    "right_hip": mp_pose.PoseLandmark.RIGHT_HIP,
    "left_knee": mp_pose.PoseLandmark.LEFT_KNEE,
    "right_knee": mp_pose.PoseLandmark.RIGHT_KNEE,
    "left_ankle": mp_pose.PoseLandmark.LEFT_ANKLE,
    "right_ankle": mp_pose.PoseLandmark.RIGHT_ANKLE,
}


def extract_pose_from_video(video_path: str, frame_sample_rate: int = 5):
    """
    Runs MediaPipe Pose over a video and returns a list of per-frame
    keypoint dictionaries: [{ "frame": i, "keypoints": {name: (x, y, visibility)} }, ...]
    frame_sample_rate: process every Nth frame (keeps it fast for a demo).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    frames_data = []
    frame_idx = 0

    with mp_pose.Pose(static_image_mode=False, model_complexity=1) as pose:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            if frame_idx % frame_sample_rate == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = pose.process(rgb_frame)

                if result.pose_landmarks:
                    keypoints = {}
                    for name, landmark_id in LANDMARK_MAP.items():
                        lm = result.pose_landmarks.landmark[landmark_id]
                        keypoints[name] = (lm.x, lm.y, lm.visibility)
                    frames_data.append({"frame": frame_idx, "keypoints": keypoints})

            frame_idx += 1

    cap.release()
    return frames_data