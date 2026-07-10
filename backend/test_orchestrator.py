from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, User, DigitalTwin, Recipient, Transaction
from app.services.orchestrator import TransactionOrchestrator
from app.core.security import get_password_hash
import json

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_orchestrator_tests():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    print("Database tables initialized.")

    try:
        # Seed test user
        pwd_hash = get_password_hash("pass123")
        user = User(
            username="robert_miller",
            email="robert@bank.com",
            hashed_password=pwd_hash,
            mpin="4321",
            balance=10000.0,
            security_score=85.0
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Initialize twin
        twin = DigitalTwin(
            user_id=user.id,
            trust_level="STABLE",
            transaction_count=5,
            avg_transaction_amount=1500.0,
            total_spend=7500.0,
            known_devices=json.dumps(["MacBook-Chrome"]),
            known_locations=json.dumps(["Seattle"]),
            trusted_recipients_count=1
        )
        db.add(twin)
        db.commit()

        # Seed recipients
        r_trusted = Recipient(user_id=user.id, name="Mary Miller (Daughter)", account_number="121212", bank_name="Chase", trust_score=95.0, is_blacklisted=False)
        r_new = Recipient(user_id=user.id, name="Unknown Seller", account_number="343434", bank_name="Wells Fargo", trust_score=75.0, is_blacklisted=False)
        r_crypto = Recipient(user_id=user.id, name="Crypto Binance OTC", account_number="565656", bank_name="Binance Pay", trust_score=40.0, is_blacklisted=False)
        r_blocked = Recipient(user_id=user.id, name="Flagged Scammer", account_number="787878", bank_name="Shadow Bank", trust_score=10.0, is_blacklisted=True)
        db.add_all([r_trusted, r_new, r_crypto, r_blocked])
        db.commit()
        db.refresh(r_trusted)
        db.refresh(r_new)
        db.refresh(r_crypto)
        db.refresh(r_blocked)

        # Seed a prior approved transaction to r_trusted so she is not "new"
        prior_tx = Transaction(
            sender_id=user.id,
            recipient_id=r_trusted.id,
            amount=1000.0,
            device="MacBook-Chrome",
            location="Seattle",
            status="APPROVED",
            risk_score=5.0,
            auth_steps_required="PASSWORD",
            auth_steps_completed="PASSWORD"
        )
        db.add(prior_tx)
        db.commit()

        orchestrator = TransactionOrchestrator()

        # Test 1: SAFE FAST-PATH BYPASS
        print("\n--- Test 1: Safe Fast-Path Transfer ---")
        res1 = orchestrator.process_transaction(
            db=db,
            sender_id=user.id,
            recipient_id=r_trusted.id,
            amount=500.0,
            device="MacBook-Chrome",
            location="Seattle"
        )
        print("Status:", res1["status"])
        print("Auth Steps Required:", res1["auth_steps_required"])
        print("Agent Logs Length:", len(res1["agent_logs"]))
        assert res1["status"] == "APPROVED"
        assert res1["auth_steps_required"] == "PASSWORD"

        # Test 2: SUSPICIOUS CHALLENGE (New recipient & high amount deviation)
        print("\n--- Test 2: Suspicious Transfer (Challenge) ---")
        res2 = orchestrator.process_transaction(
            db=db,
            sender_id=user.id,
            recipient_id=r_new.id,
            amount=6000.0, # 4x avg amount
            device="MacBook-Chrome",
            location="Seattle"
        )
        print("Status:", res2["status"])
        print("Auth Steps Required:", res2["auth_steps_required"])
        print("Triggered Rules:", res2["triggered_rules"])
        assert res2["status"] == "CHALLENGED"
        assert "MPIN" in res2["auth_steps_required"]

        # Test 3: HIGH-RISK CRYPTO (MPIN + OTP + Clarification)
        print("\n--- Test 3: High-Risk Crypto Transfer (OTP & Intent Check) ---")
        res3 = orchestrator.process_transaction(
            db=db,
            sender_id=user.id,
            recipient_id=r_crypto.id,
            amount=8000.0,
            device="MacBook-Chrome",
            location="Seattle"
        )
        print("Status:", res3["status"])
        print("Auth Steps Required:", res3["auth_steps_required"])
        print("Requires Clarification:", res3["requires_clarification"])
        print("Prompt:", res3["clarification_prompt"])
        assert res3["status"] == "CHALLENGED"
        assert "OTP" in res3["auth_steps_required"]
        assert res3["requires_clarification"] is True

        # Test 4: BLACKLISTED BLOCK
        print("\n--- Test 4: Blacklisted Recipient Block ---")
        res4 = orchestrator.process_transaction(
            db=db,
            sender_id=user.id,
            recipient_id=r_blocked.id,
            amount=100.0,
            device="MacBook-Chrome",
            location="Seattle"
        )
        print("Status:", res4["status"])
        assert res4["status"] == "BLOCKED"

        print("\nAll TransactionOrchestrator tests completed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    run_orchestrator_tests()
