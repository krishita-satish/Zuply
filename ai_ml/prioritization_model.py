import datetime
import json
import joblib
import numpy as np
from typing import Dict, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Context config (can be moved to DB or JSON file)
context_weights = {
    "festival_boost": 1.2,
    "monsoon_area_penalty": -0.3,
    "local_shortage_zones": {
        "600053": 0.5,
        "600078": 0.3
    }
}

EMERGENCY_TAGS = {"medical", "flood", "disabled", "child-only"}

DEFAULT_COOLDOWN_HOURS = {
    "small": 24,
    "large": 12
}

training_data_log: List[Dict] = []

model = None  # placeholder for trained model

# ---------------------- FEATURE EXTRACTION ----------------------
def extract_features(user: Dict, food_stock_level: int, current_time: datetime.datetime, pincode: str, is_festival: bool) -> Dict:
    hours_since_last = (current_time - user["last_donation"]).total_seconds() / 3600
    cooldown_group = "large" if user["family_size"] >= 5 else "small"
    cooldown_required = DEFAULT_COOLDOWN_HOURS[cooldown_group]

    if food_stock_level > 100:
        cooldown_required *= 0.6

    features = {
        "family_size": user["family_size"],
        "hours_since_last": hours_since_last,
        "cooldown_required": cooldown_required,
        "feedback_score": user.get("feedback_score", 3.5),
        "urgency": int(user.get("urgency_flag", False)),
        "emergency": int(user.get("special_needs", None) in EMERGENCY_TAGS),
        "is_festival": int(is_festival),
        "pincode_shortage": context_weights["local_shortage_zones"].get(pincode, 0),
        "dietary_preference_lowspice": int(user.get("dietary_preference", "") == "low-spice"),
        "food_stock_level": food_stock_level,
        "hour_of_day": current_time.hour
    }
    return features

# ---------------------- ML SCORING ----------------------
def calculate_score_from_features(features: Dict) -> Dict:
    global model
    if model is None:
        raise RuntimeError("Model not loaded or trained.")

    input_vec = np.array([list(features.values())])
    score = model.predict(input_vec)[0]

    return {"score": float(score), "explanation": ["Predicted by trained ML model"]}

# ---------------------- PROCESS REQUEST ----------------------
def process_request(user: Dict, food_stock_level: int, current_time: datetime.datetime, pincode: str, is_festival: bool = False, label_score: float = None) -> Dict:
    features = extract_features(user, food_stock_level, current_time, pincode, is_festival)
    result = calculate_score_from_features(features)

    training_entry = {
        **features,
        "user_id": user["user_id"],
        "calculated_score": result["score"],
        "label_score": label_score
    }
    training_data_log.append(training_entry)

    return {
        "user_id": user["user_id"],
        "score": result["score"],
        "explanation": result["explanation"],
        "logged": training_entry
    }

# ---------------------- TRAIN MODEL ----------------------
def train_model_from_log():
    global model
    if len(training_data_log) < 10:
        raise ValueError("Not enough training data.")

    # Convert training data
    feature_keys = [
        "family_size", "hours_since_last", "cooldown_required", "feedback_score",
        "urgency", "emergency", "is_festival", "pincode_shortage",
        "dietary_preference_lowspice", "food_stock_level", "hour_of_day"
    ]
    X = [[entry[key] for key in feature_keys] for entry in training_data_log if entry["label_score"] is not None]
    y = [entry["label_score"] for entry in training_data_log if entry["label_score"] is not None]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model trained. MSE: {mse:.2f}")

    # Save model
    with open("trained_priority_model.pkl", "wb") as f:
        joblib.dump(model, f)

# ---------------------- LOAD MODEL ----------------------
def load_trained_model(path: str = "trained_priority_model.pkl"):
    global model
    model = joblib.load(path)
    print("Model loaded successfully.")
