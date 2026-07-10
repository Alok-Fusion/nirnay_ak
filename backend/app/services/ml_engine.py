from sqlalchemy.orm import Session
from app.models.models import User, DigitalTwin, Recipient, Transaction
from datetime import datetime, timedelta, timezone
import json

class MLEngine:
    @staticmethod
    def evaluate_risk(
        db: Session,
        sender_id: int,
        recipient_id: int,
        amount: float,
        device: str,
        location: str
    ) -> dict:
        # 1. Fetch Context
        user = db.query(User).filter(User.id == sender_id).first()
        twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == sender_id).first()
        recipient = db.query(Recipient).filter(Recipient.id == recipient_id).first()
        
        if not user or not twin or not recipient:
            return {
                "risk_score": 10.0,
                "confidence": 0.5,
                "shap_values": {},
                "reason_codes": ["MISSING_CONTEXT"]
            }

        # 2. Extract History Features
        avg_amount = twin.avg_transaction_amount or 5000.0  # fallback to standard
        known_devices = json.loads(twin.known_devices or "[]")
        known_locations = json.loads(twin.known_locations or "[]")
        
        # 3. Check Velocity in last hour
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_txs_count = db.query(Transaction).filter(
            Transaction.sender_id == sender_id,
            Transaction.timestamp >= one_hour_ago
        ).count()
        
        # 4. Check recipient history
        recipient_tx_count = db.query(Transaction).filter(
            Transaction.sender_id == sender_id,
            Transaction.recipient_id == recipient_id,
            Transaction.status == "APPROVED"
        ).count()
        
        # 5. Calculate Features
        amount_ratio = amount / max(avg_amount, 100.0)
        device_match = 1 if device in known_devices else 0
        location_match = 1 if location in known_locations else 0
        recipient_trust = recipient.trust_score
        recipient_is_new = 1 if recipient_tx_count == 0 else 0
        recipient_blacklisted = 1 if recipient.is_blacklisted else 0

        # 6. SHAP & Risk Engine Mathematics
        # Baseline risk
        base_value = 10.0
        
        shap_contributions = {}
        reason_codes = []

        # Feature: Amount Deviation
        if amount_ratio > 4.0:
            shap_amount = 35.0
            reason_codes.append("UNUSUALLY_LARGE_AMOUNT")
        elif amount_ratio > 2.0:
            shap_amount = 20.0
            reason_codes.append("HIGH_AMOUNT_DEVIATION")
        elif amount_ratio < 0.2:
            shap_amount = -5.0 # Low amounts reduce overall risk slightly
        else:
            shap_amount = 0.0
        shap_contributions["Amount Deviation"] = shap_amount

        # Feature: Device Match
        if device_match == 0:
            shap_device = 20.0
            reason_codes.append("UNKNOWN_DEVICE")
        else:
            shap_device = -4.0
        shap_contributions["Device Status"] = shap_device

        # Feature: Location Match
        if location_match == 0:
            shap_location = 18.0
            reason_codes.append("GEOGRAPHIC_ANOMALY")
        else:
            shap_location = -3.0
        shap_contributions["Location Status"] = shap_location

        # Feature: Recipient Trust
        if recipient_blacklisted:
            shap_recipient = 50.0
            reason_codes.append("RECIPIENT_BLACKLISTED")
        elif recipient_trust < 30.0:
            shap_recipient = 35.0
            reason_codes.append("CRITICAL_RECIPIENT_TRUST")
        elif recipient_trust < 60.0:
            shap_recipient = 20.0
            reason_codes.append("LOW_RECIPIENT_TRUST")
        elif recipient_trust > 90.0:
            shap_recipient = -8.0 # Highly trusted recipient reduces risk
        else:
            shap_recipient = 0.0
        shap_contributions["Recipient Reputation"] = shap_recipient

        # Feature: Recipient Familiarity
        if recipient_is_new:
            shap_new_recip = 12.0
            reason_codes.append("FIRST_TIME_RECIPIENT")
        else:
            shap_new_recip = -6.0
        shap_contributions["Recipient Familiarity"] = shap_new_recip

        # Feature: Transaction Velocity
        if recent_txs_count >= 5:
            shap_velocity = 25.0
            reason_codes.append("VELOCITY_SPIKE_CRITICAL")
        elif recent_txs_count >= 2:
            shap_velocity = 10.0
            reason_codes.append("VELOCITY_SPIKE")
        else:
            shap_velocity = -2.0
        shap_contributions["Transfer Velocity"] = shap_velocity

        # Calculate final risk score (clamped between 0 and 100)
        total_shap = sum(shap_contributions.values())
        risk_score = max(0.0, min(100.0, base_value + total_shap))
        
        # Calculate model confidence (higher risk / clearer indicators increase confidence)
        confidence = 0.85
        if risk_score > 80.0 or risk_score < 15.0:
            confidence = 0.95
        elif 40.0 < risk_score < 60.0:
            confidence = 0.75

        return {
            "base_value": base_value,
            "risk_score": round(risk_score, 2),
            "confidence": confidence,
            "shap_values": shap_contributions,
            "reason_codes": reason_codes
        }
