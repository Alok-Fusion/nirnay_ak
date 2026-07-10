from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, User, DigitalTwin, Recipient, Transaction
from app.services.ml_engine import MLEngine
from app.services.digital_twin import DigitalTwinService
from app.core.security import get_password_hash
import json

# Setup in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_tests():
    # 1. Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    print("Database tables initialized in memory.")

    try:
        # 2. Seed Test User
        pwd_hash = get_password_hash("test_password_123")
        test_user = User(
            username="alex_jones",
            email="alex@capital.com",
            hashed_password=pwd_hash,
            mpin="1122",
            balance=50000.0,
            security_score=85.0
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"Created test user: {test_user.username}")

        # Initialize Digital Twin for test user
        twin = DigitalTwin(
            user_id=test_user.id,
            trust_level="NEW",
            transaction_count=0,
            avg_transaction_amount=0.0,
            total_spend=0.0,
            known_devices=json.dumps(["iPhone-iOS"]),
            known_locations=json.dumps(["San Francisco"]),
            trusted_recipients_count=0
        )
        db.add(twin)
        db.commit()
        db.refresh(twin)
        print("Initialized digital twin profile.")

        # Seed Test Recipients (one trusted, one high-risk blacklisted)
        r_trusted = Recipient(user_id=test_user.id, name="Sarah (Wife)", account_number="1234567890", bank_name="Chase", trust_score=95.0, is_blacklisted=False)
        r_scammer = Recipient(user_id=test_user.id, name="Scam OTC Broker", account_number="0987654321", bank_name="Offshore Bank", trust_score=15.0, is_blacklisted=True)
        db.add_all([r_trusted, r_scammer])
        db.commit()
        db.refresh(r_trusted)
        db.refresh(r_scammer)
        print("Seeded test recipients.")

        # 3. Test MLEngine - Normal Transaction (Sarah)
        print("\n--- Test Case 1: Low Risk Transaction ---")
        risk_result_1 = MLEngine.evaluate_risk(
            db=db,
            sender_id=test_user.id,
            recipient_id=r_trusted.id,
            amount=500.0,
            device="iPhone-iOS",
            location="San Francisco"
        )
        print("Risk Score:", risk_result_1["risk_score"])
        print("Confidence:", risk_result_1["confidence"])
        print("Reason Codes:", risk_result_1["reason_codes"])
        print("SHAP Values:", risk_result_1["shap_values"])
        assert risk_result_1["risk_score"] < 20.0, "Expected low risk for trusted recipient & matching details"

        # 4. Test MLEngine - Anomalous Transaction (Scammer)
        print("\n--- Test Case 2: High Risk Transaction (Blacklisted & Unknown Device) ---")
        risk_result_2 = MLEngine.evaluate_risk(
            db=db,
            sender_id=test_user.id,
            recipient_id=r_scammer.id,
            amount=15000.0,
            device="Ubuntu-Chrome",
            location="Unknown Region"
        )
        print("Risk Score:", risk_result_2["risk_score"])
        print("Confidence:", risk_result_2["confidence"])
        print("Reason Codes:", risk_result_2["reason_codes"])
        print("SHAP Values:", risk_result_2["shap_values"])
        assert risk_result_2["risk_score"] > 80.0, "Expected high risk for anomalous transaction"
        assert "RECIPIENT_BLACKLISTED" in risk_result_2["reason_codes"]
        assert "UNKNOWN_DEVICE" in risk_result_2["reason_codes"]

        # 5. Test DigitalTwinService Updates
        print("\n--- Test Case 3: Digital Twin Profile Updates ---")
        # Simulate successful low-risk transaction completion
        DigitalTwinService.update_profile(
            db=db,
            sender_id=test_user.id,
            transaction_amount=5000.0,
            device="MacBook-Safari",
            location="New York"
        )
        db.refresh(twin)
        print("Updated Transaction Count:", twin.transaction_count)
        print("Updated Avg Amount:", twin.avg_transaction_amount)
        print("Updated Total Spend:", twin.total_spend)
        print("Updated Known Devices:", json.loads(twin.known_devices))
        print("Updated Known Locations:", json.loads(twin.known_locations))
        
        assert twin.transaction_count == 1
        assert twin.avg_transaction_amount == 5000.0
        assert "MacBook-Safari" in json.loads(twin.known_devices)
        assert "New York" in json.loads(twin.known_locations)
        
        print("\nAll unit tests passed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    run_tests()
