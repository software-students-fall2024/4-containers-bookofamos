"""
A Flask web application for a Rock-Paper-Scissors game with AI and ML integration.
"""

import os
import time
import random
import logging
from flask import Flask, render_template, request, jsonify
import requests
from requests.exceptions import RequestException

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


def retry_request(url, files, retries=5, delay=2, timeout=10):
    """
    Retry a POST request multiple times with a delay on failure.

    Args:
        url (str): URL to send the request to.
        files (dict): Files to send in the POST request.
        retries (int): Number of retry attempts.
        delay (int): Delay between retries in seconds.
        timeout (int): Timeout for the request in seconds.

    Returns:
        Response: Response object from the successful POST request, or None if all retries fail.
    """
    for attempt in range(retries):
        try:
            response = requests.post(url, files=files, timeout=timeout)
            response.raise_for_status()
            return response
        except RequestException as error:
            logging.warning("Retry attempt %d failed: %s", attempt + 1, str(error))
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                logging.error("All retry attempts failed.")
                return None
    return None


@app.route("/")
def home():
    """Render the home page."""
    return render_template("title.html")


@app.route("/index")
def index():
    """Render the index page."""
    return render_template("index.html")


@app.route("/statistics")
def statistics():
    """Render the statistics page."""
    return render_template("statistics.html")


@app.route("/result", methods=["POST"])
def result():
    """
    Handle the result of the Rock-Paper-Scissors game.

    Accepts an image from the user, sends it to the machine learning client
    for gesture prediction, and returns the game result.
    """
    app.logger.debug("Received request at /result")
    try:
        if "image" not in request.files:
            app.logger.error("No image file provided")
            return jsonify({"error": "No image file provided"}), 400

        file = request.files["image"]
        ml_client_url = os.getenv(
            "ML_CLIENT_URL", "http://machine-learning-client:5000"
        )
        app.logger.debug("Sending image to ML client at %s/predict", ml_client_url)
        response = retry_request(f"{ml_client_url}/predict", files={"image": file})
        if not response:
            app.logger.error("ML client did not respond")
            return render_template(
                "result.html",
                user="Unknown",
                ai=random.choice(["Rock", "Paper", "Scissors"]),
                result="No valid prediction. Please try again.",
            )
        user_gesture = response.json().get("gesture", "Unknown")
        if user_gesture == "Unknown":
            app.logger.warning("Prediction returned 'Unknown'.")
            return render_template(
                "result.html",
                user="Unknown",
                ai=random.choice(["Rock", "Paper", "Scissors"]),
                result="Gesture not recognized. Please try again.",
            )
    except RequestException as error:
        app.logger.error("Error communicating with ML client: %s", str(error))
        return jsonify({"error": "Error communicating with ML client"}), 500

    ai_gesture = random.choice(["Rock", "Paper", "Scissors"])
    game_result = determine_winner(user_gesture, ai_gesture)
    app.logger.debug("Game result: %s", game_result)
    return render_template(
        "result.html", user=user_gesture, ai=ai_gesture, result=game_result
    )


def determine_winner(user, ai_choice):
    """
    Determine the winner of the Rock-Paper-Scissors game.

    Args:
        user (str): User's gesture.
        ai_choice (str): AI's gesture.

    Returns:
        str: Result of the game.
    """
    winning_cases = {
        "Rock": "Scissors",
        "Paper": "Rock",
        "Scissors": "Paper",
    }
    if user == ai_choice:
        return "It's a tie!"
    if ai_choice == winning_cases.get(user):
        return "You win!"
    return "AI wins!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
