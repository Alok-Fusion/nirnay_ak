from sqlalchemy.orm import Session
from app.models.models import User, DigitalTwin, Recipient, Transaction
from datetime import datetime, timezone
import json

class DigitalTwinService:
    @staticmethod
    def update_profile(db: Session, sender_id: int, transaction_amount: float, device: str, location: str):
        # 1. Fetch User and Digital Twin
        user = db.query(User).filter(User.id == sender_id).first()
        twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == sender_id).first()
        
        if not user or not twin:
            return None

        # 2. Update Basic Metrics
        twin.transaction_count += 1
        twin.total_spend += transaction_amount
        twin.avg_transaction_amount = round(twin.total_spend / twin.transaction_count, 2)

        # 3. Update Devices
        try:
            devices = json.loads(twin.known_devices or "[]")
        except Exception:
            devices = []
        if device not in devices:
            devices.append(device)
            twin.known_devices = json.dumps(devices)

        # 4. Update Locations
        try:
            locations = json.loads(twin.known_locations or "[]")
        except Exception:
            locations = []
        if location not in locations:
            locations.append(location)
            twin.known_locations = json.dumps(locations)

        # 5. Update Trusted Recipients Count
        # We consider a recipient trusted if trust_score >= 80
        trusted_count = db.query(Recipient).filter(
            Recipient.user_id == sender_id,
            Recipient.trust_score >= 80.0
        ).count()
        twin.trusted_recipients_count = trusted_count

        # 6. Evolve Trust Level Tier
        # NEW -> STABLE -> HIGHLY_TRUSTED
        if twin.transaction_count >= 10 and user.security_score >= 90.0:
            twin.trust_level = "HIGHLY_TRUSTED"
        elif twin.transaction_count >= 5:
            twin.trust_level = "STABLE"
        else:
            twin.trust_level = "NEW"

        twin.updated_at = datetime.now(timezone.utc)
        db.add(twin)
        db.commit()
        db.refresh(twin)
        
        # 7. Dynamically adjust user's security score based on history
        # As they complete transactions successfully, their security score improves slightly
        if user.security_score < 98.0:
            user.security_score = min(98.0, user.security_score + 0.5)
            db.add(user)
            db.commit()
            
        return twin
