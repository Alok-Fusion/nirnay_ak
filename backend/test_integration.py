import os
os.environ["NIRNAY_TEST_MODE"] = "true"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, User, Recipient, Transaction, AuditLog, DigitalTwin
from app.api.auth import register, login_json
from app.api.recipients import create_recipient, list_recipients
from app.api.transactions import initiate_transaction, authenticate_challenge, submit_clarification
from app.api.dashboard import get_dashboard_summary
from app.schemas.schemas import UserCreate, RecipientCreate, TransactionInitiate, TransactionAuthChallenge, TransactionClarification, UserLogin
import json

# Setup in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def run_integration_tests():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    print("Database tables initialized for API integration testing.")

    try:
        # 1. Register User (Triggering DB seed history)
        print("\n--- Step 1: User Registration & Auto Seeding History ---")
        reg_data = UserCreate(
            username="alok_kumar",
            email="alok@fusion.com",
            password="SecurePassword123!",
            mpin="9999",
            full_name="Alok Kumar",
            phone="9876543210",
            address="123 Financial District, Mumbai",
            aadhaar_number="123456789012",
            pan_number="ABCDE1234F"
        )
        reg_response = register(user_in=reg_data, db=db)
        print("Registration access token generated:", reg_response["access_token"])
        
        # Verify the user exists
        user = db.query(User).filter(User.username == "alok_kumar").first()
        assert user is not None
        print("Registered User ID:", user.id)
        print("Initial Balance:", user.balance)
        print("Initial Security Score:", user.security_score)

        # Check seeded recipients
        seeded_recipients = list_recipients(db=db, current_user=user)
        print(f"Seeded recipients count: {len(seeded_recipients)}")
        for r in seeded_recipients:
            print(f"  - Beneficiary: {r.name} (Bank: {r.bank_name}) | Trust Score: {r.trust_score}")
        assert len(seeded_recipients) >= 2

        # 2. Get Dashboard Summary
        print("\n--- Step 2: Retrieve Dashboard summary ---")
        dash = get_dashboard_summary(db=db, current_user=user)
        print("Dashboard summary details:")
        print("  - Total Balance:", dash["balance"])
        print("  - Trust Level Tier:", dash["trust_level"])
        print("  - Security Health:", dash["security_score"])
        print("  - Total Transaction History Count:", len(dash["recent_transactions"]))
        assert dash["balance"] == 150000.0
        assert len(dash["recent_transactions"]) == 4

        # 3. Create a custom recipient
        print("\n--- Step 3: Add new transaction recipient ---")
        new_recip_data = RecipientCreate(name="Crypto Exchange CoinDesk", account_number="99887766", bank_name="Shadow Crypto Bank")
        r_new = create_recipient(recipient=new_recip_data, db=db, current_user=user)
        print(f"Recipient added: {r_new.name} | ID: {r_new.id} | Trust score: {r_new.trust_score}")
        assert r_new.name == "Crypto Exchange CoinDesk"

        # 4. Initiate Transaction to Crypto Recipient
        print("\n--- Step 4: Initiate transaction to Crypto Recipient ---")
        tx_init_data = TransactionInitiate(recipient_id=r_new.id, amount=12000.0, device="Windows-Firefox", location="Delhi")
        tx_result = initiate_transaction(tx_in=tx_init_data, db=db, current_user=user)
        print("Transaction execution state:")
        print("  - Status:", tx_result["status"])
        print("  - Calculated Risk Score:", tx_result["risk_score"])
        print("  - Required Challenge Steps:", tx_result["auth_steps_required"])
        print("  - Clarification prompt:", tx_result["clarification_prompt"])
        
        tx_id = tx_result["transaction_id"]
        assert tx_result["status"] == "CHALLENGED"
        assert "OTP" in tx_result["auth_steps_required"]
        assert tx_result["requires_clarification"] is True

        # 5. Authenticate challenge factors (Simulate MPIN & OTP)
        print("\n--- Step 5: Authenticating Factors (MPIN + OTP) ---")
        auth_data = TransactionAuthChallenge(transaction_id=tx_id, mpin="9999", otp="123456")
        auth_res = authenticate_challenge(challenge=auth_data, db=db, current_user=user)
        print("Auth check message:", auth_res["message"])
        print("Auth check status:", auth_res["status"])
        assert auth_res["status"] == "AWAITING_CLARIFICATION" # Verified steps but still needs clarification

        # 6. Submit clarification natural language statement
        print("\n--- Step 6: Submitting Natural Language Clarification ---")
        clar_data = TransactionClarification(transaction_id=tx_id, response_text="I am buying ethereum for my personal wallet. I want to hold it long-term.")
        clar_res = submit_clarification(clarification=clar_data, db=db, current_user=user)
        print("Clarification message:", clar_res["message"])
        print("Clarification status:", clar_res["status"])
        assert clar_res["status"] == "APPROVED"

        # 7. Check post-transaction balance and history
        db.refresh(user)
        print("\n--- Step 7: Final state verification ---")
        print("New User balance:", user.balance)
        assert user.balance == 150000.0 - 12000.0
        
        # Verify transaction status in db
        tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
        assert tx.status == "APPROVED"
        print("Transaction executed successfully in DB.")
        
        print("\nAll API route integration tests passed successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    run_integration_tests()
