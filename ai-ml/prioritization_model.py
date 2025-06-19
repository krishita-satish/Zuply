import datetime
import json
from typing import Dict, List

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

# Mock database for training data collection (replace with real DB logic)
training_data_log: List[Dict] = []

def extract_features(user: Dict, food_stock_level: int, current_time: datetime.datetime, pincode: str, is_festival: bool) -> Dict:
    """Extracts features from input data."""
    hours_since_last = (current_time - user["last_donation"]).total_seconds() / 3600
    cooldown_group = "large" if user["family_size"] >= 5 else "small"
    cooldown_required = DEFAULT_COOLDOWN_HOURS[cooldown_group]
    
    if food_stock_level > 100:
        cooldown_required *= 0.6  # dynamic cooldown
    
    features = {
        "family_size": user["family_size"],
        "hours_since_last": hours_since_last,
        "cooldown_required": cooldown_required,
        "feedback_score": user.get("feedback_score", 3.5),
        "urgency": user.get("urgency_flag", False),
        "special_needs": user.get("special_needs", None),
        "is_festival": is_festival,
        "pincode": pincode,
        "dietary_preference": user.get("dietary_preference", ""),
        "food_stock_level": food_stock_level,
        "hour_of_day": current_time.hour
    }
    return features

def calculate_score_from_features(features: Dict) -> Dict:
    """Scores a request using business rules."""
    score = 0
    reason = []

    # 1. Family Size
    if features["family_size"] >= 5:
        score += 5
        reason.append("Large family boosted")
    else:
        score += 3
        reason.append("Small/medium family")

    # 2. Cooldown logic
    if features["hours_since_last"] >= features["cooldown_required"]:
        score += 4
        reason.append("Eligible (cooldown passed)")
    else:
        score -= 5
        reason.append("Cooldown active")

    # 3. Feedback
    score += features["feedback_score"] - 3.0
    reason.append(f"Feedback score {features['feedback_score']}")

    # 4. Emergency
    if features["urgency"] or features["special_needs"] in EMERGENCY_TAGS:
        score += 10
        reason.append("Emergency escalation triggered")

    # 5. Context: festival or local shortage
    if features["is_festival"]:
        score += context_weights.get("festival_boost", 1.0)
        reason.append("Festival context boost")
    if features["pincode"] in context_weights["local_shortage_zones"]:
        boost = context_weights["local_shortage_zones"][features["pincode"]]
        score += boost
        reason.append(f"Local shortage boost: {boost}")

    # 6. Time-of-day penalty
    if 13 <= features["hour_of_day"] <= 15:
        score -= 1
        reason.append("Time-of-day penalty (hot hour)")

    # 7. Diet preference
    if features["dietary_preference"] == "low-spice":
        score += 1
        reason.append("Low-spice meal matched")

    return {"score": score, "explanation": reason}

def process_request(user: Dict, food_stock_level: int, current_time: datetime.datetime, pincode: str, is_festival: bool = False, label_score: float = None) -> Dict:
    """Processes a donation request."""
    features = extract_features(user, food_stock_level, current_time, pincode, is_festival)
    result = calculate_score_from_features(features)

    # Save for ML training
    training_entry = {
        **features,
        "user_id": user["user_id"],
        "calculated_score": result["score"],
        "label_score": label_score  # optional: real score from admin decision
    }
    training_data_log.append(training_entry)

    return {
        "user_id": user["user_id"],
        "score": result["score"],
        "explanation": result["explanation"],
        "logged": training_entry
    }
