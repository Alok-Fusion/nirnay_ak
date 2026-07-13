from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime
import re

# Authentication Schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    mpin: str = Field(..., min_length=4, max_length=6, description="MPIN must be 4 to 6 digits")
    full_name: str
    phone: str
    address: str
    aadhaar_number: str = Field(..., min_length=12, max_length=12)
    pan_number: str = Field(..., min_length=10, max_length=10)
    driving_license: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[^a-zA-Z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('aadhaar_number')
    @classmethod
    def validate_aadhaar(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('Aadhaar number must contain only digits')
        return v

    @field_validator('pan_number')
    @classmethod
    def validate_pan(cls, v: str) -> str:
        v_upper = v.upper()
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', v_upper):
            raise ValueError('Invalid PAN format (expected e.g. ABCDE1234F)')
        return v_upper

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    balance: float
    security_score: float
    created_at: datetime
    
    # KYC & Banking fields
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    aadhaar_last4: Optional[str] = None
    pan_number: Optional[str] = None
    driving_license: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None
    is_tour_completed: bool
    is_frozen: bool
    daily_transfer_limit: float

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserProfileUpdate(BaseModel):
    phone: str
    address: str
    email: EmailStr

# Recipient Schemas
class RecipientCreate(BaseModel):
    name: str
    account_number: str
    bank_name: str

class RecipientOut(BaseModel):
    id: int
    user_id: int
    name: str
    account_number: str
    bank_name: str
    trust_score: float
    is_blacklisted: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Transaction Schemas
class TransactionInitiate(BaseModel):
    recipient_id: int
    amount: float = Field(..., gt=0)
    device: str
    location: str

class TransactionOut(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    amount: float
    device: str
    location: str
    timestamp: datetime
    status: str
    risk_score: float
    explanation: Optional[str] = None
    auth_steps_required: str
    auth_steps_completed: str
    recipient: Optional[RecipientOut] = None

    class Config:
        from_attributes = True

class TransactionAuthChallenge(BaseModel):
    transaction_id: int
    password: Optional[str] = None
    mpin: Optional[str] = None
    otp: Optional[str] = None

class TransactionClarification(BaseModel):
    transaction_id: int
    response_text: str

# Dashboard / Security Center
class DigitalTwinOut(BaseModel):
    trust_level: str
    transaction_count: int
    avg_transaction_amount: float
    total_spend: float
    known_devices: List[str]
    known_locations: List[str]
    trusted_recipients_count: int

class DashboardSummary(BaseModel):
    balance: float
    security_score: float
    trust_level: str
    transaction_count: int
    recent_transactions: List[TransactionOut]

# Admin
class AdminOverrideRequest(BaseModel):
    transaction_id: int
    action: str # FORCE_APPROVE or FORCE_BLOCK

# Neo-Banking Schemas
class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0)
    category: str # UPI_RECEIVE, BANK_TRANSFER, SALARY, REFUND

class P2PTransferRequest(BaseModel):
    recipient_account_number: str
    amount: float = Field(..., gt=0)
    device: str
    location: str

class LedgerEntryOut(BaseModel):
    id: int
    type: str
    category: str
    amount: float
    balance_after: float
    description: str
    reference_id: Optional[str] = None
    counterparty: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class SecurityLogOut(BaseModel):
    id: int
    event_type: str
    ip_address: Optional[str] = None
    device: Optional[str] = None
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class UpdateLimitRequest(BaseModel):
    limit: float = Field(..., gt=0)
    mpin: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# Banking Products (Cards, FDs, Offers)
class VirtualCardCreate(BaseModel):
    card_type: str # VISA_DEBIT, MASTERCARD_PREMIUM
    spend_limit: float = Field(50000.0, gt=0)

class VirtualCardOut(BaseModel):
    id: int
    user_id: int
    card_number: str
    expiry_date: str
    cvv: str
    card_holder: str
    status: str
    card_type: str
    spend_limit: float
    total_spent: float
    created_at: datetime

    class Config:
        from_attributes = True

class CardLimitUpdate(BaseModel):
    spend_limit: float = Field(..., gt=0)

class FixedDepositCreate(BaseModel):
    principal_amount: float = Field(..., gt=0)
    duration_months: int = Field(..., ge=1, le=120)

class FixedDepositOut(BaseModel):
    id: int
    user_id: int
    principal_amount: float
    interest_rate: float
    duration_months: int
    maturity_amount: float
    status: str
    created_at: datetime
    matures_at: datetime

    class Config:
        from_attributes = True

class OfferOut(BaseModel):
    id: str
    title: str
    description: str
    reward_rate: str
    category: str
    unlocked: bool
    unlock_score: float
