import os
import sys
import unittest
from datetime import datetime, timezone, timedelta

# Add backend dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.models import User, VirtualCard, FixedDeposit, LedgerEntry
from app.api.banking_products import router

class TestBankingProducts(unittest.TestCase):
    def setUp(self):
        # Create SQLite in-memory database
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = TestingSessionLocal()

        # Create dummy user
        self.user = User(
            username="alex_jones",
            email="alex@gmail.com",
            hashed_password="hashed_password",
            balance=100000.0,
            security_score=85.0,
            full_name="Alex Jones",
            account_number="123456789012"
        )
        self.db.add(self.user)
        self.db.commit()
        self.db.refresh(self.user)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_create_virtual_card(self):
        # Create cards
        card_1 = VirtualCard(
            user_id=self.user.id,
            card_number="4532111122223333",
            expiry_date="12/28",
            cvv="123",
            card_holder="Alex Jones",
            status="ACTIVE",
            card_type="VISA_DEBIT"
        )
        self.db.add(card_1)
        self.db.commit()

        # Check total cards
        cnt = self.db.query(VirtualCard).filter(VirtualCard.user_id == self.user.id).count()
        self.assertEqual(cnt, 1)

    def test_create_fixed_deposit(self):
        principal = 20000.0
        duration = 12
        rate = 7.0
        maturity = principal * (1 + (rate / 100.0) * (duration / 12.0))

        # Check balance pre-FD
        self.assertEqual(self.user.balance, 100000.0)

        # Deduct principal
        self.user.balance -= principal
        self.db.add(self.user)

        # Create FD
        fd = FixedDeposit(
            user_id=self.user.id,
            principal_amount=principal,
            interest_rate=rate,
            duration_months=duration,
            maturity_amount=maturity,
            status="ACTIVE",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
            matures_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=365)
        )
        self.db.add(fd)
        self.db.commit()

        # Check balance post-FD
        self.assertEqual(self.user.balance, 80000.0)
        self.assertEqual(fd.maturity_amount, 21400.0)

if __name__ == "__main__":
    unittest.main()
