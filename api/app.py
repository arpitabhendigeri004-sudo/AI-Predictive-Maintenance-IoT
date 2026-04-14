from flask import Flask, request, jsonify
import joblib
import numpy as np

# Initialize Flask app
app = Flask(__name__)

# Load trained model
try:
    model = joblib.load("../models/model.pkl")
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Error loading model:", e)
    model = None


# Home route (for testing)
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "AI Predictive Maintenance API is running 🚀"
    })


# Prediction route
@app.route("/predict", methods=["POST"])
def predict():
    try:
        if model is None:
            return jsonify({"error": "Model not loaded"}), 500

        data = request.get_json()

        # Validate input
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        temperature = data.get("temperature")
        vibration = data.get("vibration")
        current = data.get("current")

        if temperature is None or vibration is None or current is None:
            return jsonify({"error": "Missing input values"}), 400

        # Convert to numpy array
        features = np.array([[temperature, vibration, current]])

        # Prediction
        prediction = model.predict(features)[0]

        # Probability (confidence)
        try:
            prob = model.predict_proba(features)[0][1]
            confidence = round(prob * 100, 2)
        except:
            confidence = 0.0

        # Result label
        result = "Failure Likely ⚠️" if prediction == 1 else "Normal ✅"

        return jsonify({
            "prediction": result,
            "confidence": confidence,
            "input": {
                "temperature": temperature,
                "vibration": vibration,
                "current": current
            }
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# Run app
if __name__ == "__main__":
    app.run(debug=True)