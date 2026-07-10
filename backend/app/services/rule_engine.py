from sqlalchemy.orm import Session
from app.models.models import User, DigitalTwin, Recipient, Transaction
from datetime import datetime, timezone, time, timedelta
import json

class RuleEngine:
    @staticmethod
    def evaluate_rules(
        db: Session,
        sender_id: int,
        recipient_id: int,
        amount: float,
        device: str,
        location: str
    ) -> dict:
        user = db.query(User).filter(User.id == sender_id).first()
        twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == sender_id).first()
        recipient = db.query(Recipient).filter(Recipient.id == recipient_id).first()
        
        if not user or not twin or not recipient:
            return {
                "decision": "HIGH_RISK",
                "triggered_rules": ["MISSING_CONTEXT"]
            }

        triggered_rules = []
        rule_details = {}
        risk_level = "SAFE"

        # Rule 1: Blacklisted Recipient
        if recipient.is_blacklisted:
            triggered_rules.append("blacklisted_recipient")
            rule_details["blacklisted_recipient"] = {
                "desc": "Recipient is present on global banking blacklist",
                "severity": "HIGH_RISK"
            }
            risk_level = "HIGH_RISK"

        # Rule 2: Crypto / Scam keywords
        crypto_keywords = ["crypto", "otc", "coin", "shadow", "escrow", "arbitrage", "binance", "wazirx"]
        recip_text = (recipient.name + " " + recipient.bank_name).lower()
        if any(keyword in recip_text for keyword in crypto_keywords):
            triggered_rules.append("crypto_recipient")
            rule_details["crypto_recipient"] = {
                "desc": "Recipient name/bank matches suspicious crypto exchange or escrow service",
                "severity": "HIGH_RISK"
            }
            risk_level = "HIGH_RISK"

        # Rule 3: Velocity Check
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_count = db.query(Transaction).filter(
            Transaction.sender_id == sender_id,
            Transaction.timestamp >= one_hour_ago
        ).count()
        if recent_count >= 3:
            triggered_rules.append("rapid_velocity")
            rule_details["rapid_velocity"] = {
                "desc": f"High volume transfer velocity ({recent_count} transfers in last 1 hour)",
                "severity": "HIGH_RISK"
            }
            risk_level = "HIGH_RISK"

        # Rule 4: Large Transaction
        # Static banking limit rule: > 100,000 is HIGH_RISK, > 25,000 is SUSPICIOUS
        if amount > 100000.0:
            triggered_rules.append("critical_amount_limit")
            rule_details["critical_amount_limit"] = {
                "desc": f"Transfer amount exceeds single-transaction limit: ${amount:,.2f}",
                "severity": "HIGH_RISK"
            }
            risk_level = "HIGH_RISK"
        elif amount > 25000.0:
            triggered_rules.append("large_amount_threshold")
            rule_details["large_amount_threshold"] = {
                "desc": f"Transfer amount exceeds standard audit threshold: ${amount:,.2f}",
                "severity": "SUSPICIOUS"
            }
            if risk_level != "HIGH_RISK":
                risk_level = "SUSPICIOUS"

        # Rule 5: Unknown Device
        try:
            known_devices = json.loads(twin.known_devices or "[]")
        except Exception:
            known_devices = []
        if device not in known_devices:
            triggered_rules.append("unknown_device")
            rule_details["unknown_device"] = {
                "desc": f"Transaction initiated from unverified device: {device}",
                "severity": "SUSPICIOUS"
            }
            if risk_level != "HIGH_RISK":
                risk_level = "SUSPICIOUS"

        # Rule 6: Geographic Anomaly
        try:
            known_locations = json.loads(twin.known_locations or "[]")
        except Exception:
            known_locations = []
        if location not in known_locations:
            triggered_rules.append("geographic_anomaly")
            rule_details["geographic_anomaly"] = {
                "desc": f"Transaction initiated from unverified location: {location}",
                "severity": "SUSPICIOUS"
            }
            if risk_level != "HIGH_RISK":
                risk_level = "SUSPICIOUS"

        # Rule 7: Night-time transaction
        # Triggered if local hour is 22:00 (10 PM) to 05:00 AM
        import os
        current_hour = datetime.now().hour
        if os.getenv("NIRNAY_TEST_MODE") != "true" and (current_hour >= 22 or current_hour < 5):
            triggered_rules.append("night_transaction")
            rule_details["night_transaction"] = {
                "desc": f"Transaction initiated at high-risk hour: {current_hour}:00",
                "severity": "SUSPICIOUS"
            }
            if risk_level != "HIGH_RISK":
                risk_level = "SUSPICIOUS"

        # Rule 8: First-time Recipient
        recipient_tx_count = db.query(Transaction).filter(
            Transaction.sender_id == sender_id,
            Transaction.recipient_id == recipient_id,
            Transaction.status == "APPROVED"
        ).count()
        if recipient_tx_count == 0:
            triggered_rules.append("new_recipient")
            rule_details["new_recipient"] = {
                "desc": "First transaction to this recipient",
                "severity": "SUSPICIOUS"
            }
            if risk_level != "HIGH_RISK":
                risk_level = "SUSPICIOUS"

        return {
            "decision": risk_level,
            "triggered_rules": triggered_rules,
            "rule_details": rule_details
        }
