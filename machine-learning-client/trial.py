"""
Flask application for predicting Rock-Paper-Scissors gestures using a TensorFlow model.
"""

from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model  # pylint: disable=E0401,E0611
import cv2  # pylint: disable=E1101
import numpy as np
import mediapipe as mp


app = Flask(__name__)

MODEL_PATH = "model/rock_paper_scissors_model.h5"
model = load_model(MODEL_PATH)
CLASS_LABELS = ["Rock", "Paper", "Scissors"]

def get_finger_status(hands_module, hand_landmarks, finger_name):
    finger_id_map = {'INDEX': 8, 'MIDDLE': 12, 'RING': 16, 'PINKY': 20}

    finger_tip_y = hand_landmarks.landmark[finger_id_map[finger_name]].y
    finger_dip_y = hand_landmarks.landmark[finger_id_map[finger_name] - 1].y
    finger_mcp_y = hand_landmarks.landmark[finger_id_map[finger_name] - 2].y

    return finger_tip_y < finger_mcp_y


def get_thumb_status(hands_module, hand_landmarks):
    thumb_tip_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP].x
    thumb_mcp_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP - 2].x
    thumb_ip_x = hand_landmarks.landmark[hands_module.HandLandmark.THUMB_TIP - 1].x

    return thumb_tip_x > thumb_ip_x > thumb_mcp_x

@app.route("/predict", methods=["POST"])
def predict():
    """
    Predict the gesture in the uploaded image using the trained model.

    Returns:
        JSON response with the predicted gesture or error message.
    """
    try:
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files["image"]
        
        image = cv2.imdecode(  # pylint: disable=E1101
                        np.frombuffer(file.stream.read(), np.uint8),
                        cv2.IMREAD_COLOR,  # pylint: disable=E1101
                    )
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_hands = mp.solutions.hands
        with mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5) as hands:
            
            
            move = "UNKNOWN"
            results = hands.process(mp_image)
            for hand_landmarks in results.multi_hand_landmarks:
                current_state = ""
                thumb_status = get_thumb_status(mp_hands, hand_landmarks)
                current_state += "1" if thumb_status else "0"

                index_status = get_finger_status(mp_hands, hand_landmarks, 'INDEX')
                current_state += "1" if index_status else "0"

                middle_status = get_finger_status(mp_hands, hand_landmarks, 'MIDDLE')
                current_state += "1" if middle_status else "0"

                ring_status = get_finger_status(mp_hands, hand_landmarks, 'RING')
                current_state += "1" if ring_status else "0"

                pinky_status = get_finger_status(mp_hands, hand_landmarks, 'PINKY')
                current_state += "1" if pinky_status else "0"

                if current_state == "00000":
                    move = "Rock"
                elif current_state == "11111":
                    move = "Paper"
                elif current_state == "01100":
                    move = "Scissors"
                else:
                    move = "UNKNOWN"

        

        

        return jsonify({"gesture": move})
    except KeyError as error:
        return jsonify({"error": f"Key error: {str(error)}"}), 400
    except ValueError as error:
        return jsonify({"error": f"Value error: {str(error)}"}), 400
    except RuntimeError as error:
        return jsonify({"error": f"Runtime error: {str(error)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
