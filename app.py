import cv2
import numpy as np
import mediapipe as mp
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av

# Initialize MediaPipe Pose
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Function to calculate angle
def calculate_angle(a, b, c):
    a = np.array(a)  # First
    b = np.array(b)  # Mid
    c = np.array(c)  # End

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

# Session state for counter and stage
if 'counter' not in st.session_state:
    st.session_state.counter = 0
if 'stage' not in st.session_state:
    st.session_state.stage = None
if 'view' not in st.session_state:
    st.session_state.view = None
if 'form_status' not in st.session_state:
    st.session_state.form_status = "Unknown"
if 'warning_message' not in st.session_state:
    st.session_state.warning_message = ""

# Video processor callback
def video_processor(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format="bgr24")

    # Process with MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    # Extract landmarks and perform logic
    try:
        landmarks = results.pose_landmarks.landmark

        if not landmarks:
            raise ValueError("No landmarks detected")

        # Calculate average visibilities for left and right sides
        left_vis = (
            landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].visibility +
            landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].visibility +
            landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].visibility
        ) / 3

        right_vis = (
            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].visibility +
            landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].visibility +
            landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].visibility
        ) / 3

        # Determine view
        if left_vis > 0.6 and right_vis > 0.6:
            st.session_state.view = "front"
        elif left_vis > 0.6:
            st.session_state.view = "side_left"
        elif right_vis > 0.6:
            st.session_state.view = "side_right"
        else:
            st.session_state.view = "unknown"
            st.session_state.warning_message = "Improper placement or low light"
            st.session_state.form_status = "Unknown"
            cv2.putText(image, st.session_state.warning_message, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
            raise ValueError("Unknown view")

        # Check distance
        distance_status = ""
        if st.session_state.view == "front":
            shoulder_dist = abs(
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x -
                landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x
            )
            if shoulder_dist < 0.15:
                distance_status = "Too far from camera"
            elif shoulder_dist > 0.6:
                distance_status = "Too close to camera"
        elif st.session_state.view in ["side_left", "side_right"]:
            side_prefix = "LEFT" if st.session_state.view == "side_left" else "RIGHT"
            sh_idx = mp_pose.PoseLandmark[f"{side_prefix}_SHOULDER"].value
            hp_idx = mp_pose.PoseLandmark[f"{side_prefix}_HIP"].value
            sh = landmarks[sh_idx]
            hp = landmarks[hp_idx]
            torso_dist = np.sqrt((sh.x - hp.x)**2 + (sh.y - hp.y)**2)
            if torso_dist < 0.2:
                distance_status = "Too far from camera"
            elif torso_dist > 0.7:
                distance_status = "Too close to camera"

        if distance_status:
            st.session_state.warning_message = distance_status
            cv2.putText(image, st.session_state.warning_message, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

        # Check form (body straight)
        good_form = False
        if st.session_state.view == "front":
            # Check both sides
            left_hip_angle = calculate_angle(
                [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y],
                [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y],
                [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            )
            right_hip_angle = calculate_angle(
                [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y],
                [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y],
                [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            )
            if abs(left_hip_angle - 180) < 30 and abs(right_hip_angle - 180) < 30:
                good_form = True
        else:
            # Side view, check visible side
            side_prefix = "LEFT" if st.session_state.view == "side_left" else "RIGHT"
            sh_idx = mp_pose.PoseLandmark[f"{side_prefix}_SHOULDER"].value
            hp_idx = mp_pose.PoseLandmark[f"{side_prefix}_HIP"].value
            an_idx = mp_pose.PoseLandmark[f"{side_prefix}_ANKLE"].value
            hip_angle = calculate_angle(
                [landmarks[sh_idx].x, landmarks[sh_idx].y],
                [landmarks[hp_idx].x, landmarks[hp_idx].y],
                [landmarks[an_idx].x, landmarks[an_idx].y]
            )
            if abs(hip_angle - 180) < 30:
                good_form = True

        st.session_state.form_status = "Good" if good_form else "Bad - Straighten body"

        # Pushup counter logic
        if st.session_state.view == "front":
            avg_shoulder_y = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y + landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y) / 2
            avg_elbow_y = (landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y + landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y) / 2
            if avg_shoulder_y > avg_elbow_y + 0.02:
                st.session_state.stage = "down"
            if avg_shoulder_y < avg_elbow_y - 0.02 and st.session_state.stage == "down":
                st.session_state.stage = "up"
                if good_form:
                    st.session_state.counter += 1
        else:
            # Side view
            side_prefix = "LEFT" if st.session_state.view == "side_left" else "RIGHT"
            sh_idx = mp_pose.PoseLandmark[f"{side_prefix}_SHOULDER"].value
            el_idx = mp_pose.PoseLandmark[f"{side_prefix}_ELBOW"].value
            wr_idx = mp_pose.PoseLandmark[f"{side_prefix}_WRIST"].value

            shoulder = [landmarks[sh_idx].x, landmarks[sh_idx].y]
            elbow = [landmarks[el_idx].x, landmarks[el_idx].y]
            wrist = [landmarks[wr_idx].x, landmarks[wr_idx].y]

            angle = calculate_angle(shoulder, elbow, wrist)

            # Visualize angle
            cv2.putText(image, str(int(angle)),
                        tuple(np.multiply(elbow, [image.shape[1], image.shape[0]]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            if angle < 100:
                st.session_state.stage = "down"
            if angle > 150 and st.session_state.stage == "down":
                st.session_state.stage = "up"
                if good_form:
                    st.session_state.counter += 1

    except Exception as e:
        pass

    # Render pushup counter on image
    # Setup status box
    cv2.rectangle(image, (0, 0), (300, 100), (245, 117, 16), -1)

    # Rep data
    cv2.putText(image, 'REPS', (15, 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, str(st.session_state.counter),
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

    # Stage data
    cv2.putText(image, 'STAGE', (95, 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, st.session_state.stage if st.session_state.stage else "N/A",
                (90, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

    # Form data
    cv2.putText(image, 'FORM', (185, 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, st.session_state.form_status,
                (170, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2, cv2.LINE_AA)

    # Draw landmarks
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

    return av.VideoFrame.from_ndarray(image, format="bgr24")

# Streamlit app
st.title("Pushup Counter App")

# Button to reset counter
if st.button("Reset Counter"):
    st.session_state.counter = 0
    st.session_state.stage = None

# Display current counter (optional, since it's on video)
st.write(f"Current Reps: {st.session_state.counter}")

# WebRTC streamer
webrtc_streamer(
    key="pushup_counter",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=video_processor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

st.info("Note: Make sure to install required libraries: pip install streamlit streamlit-webrtc opencv-python mediapipe numpy")