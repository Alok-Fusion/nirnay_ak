# NIRNAY: AI-Protected Neo-Banking & Autonomous Decision Intelligence Platform

> **Tagline:** Moving Beyond Passive Fraud Detection. Entering the Era of Autonomous Decision Protection.

---

## 📌 Table of Contents
1. [Executive Summary & Problem Statement](#-executive-summary--problem-statement)
2. [Platform Architecture & Core Flow](#-platform-architecture--core-flow)
3. [Deep-Dive Feature Catalog](#-deep-dive-feature-catalog)
   - [AI & Social Engineering Protection Core](#ai--social-engineering-protection-core)
   - [Neo-Banking Operations & Ledger System](#neo-banking-operations--ledger-system)
   - [Enterprise Security Controls](#enterprise-security-controls)
   - [Unique Strategic Capabilities](#unique-strategic-capabilities)
4. [API Endpoints Reference](#-api-endpoints-reference)
5. [Database Models & Schemas](#-database-models--schemas)
6. [Detailed Installation & Setup Guide](#-detailed-installation--setup-guide)
7. [Verification & Testing Suite](#-verification--testing-suite)

---

## 🎯 Executive Summary & Problem Statement

Modern digital banking systems suffer from a critical flaw: **traditional fraud detection is reactive, binary, and easily bypassed by social engineering.** When a victim is coached by a scammer over a call, they complete standard multi-factor authentication (OTP, MPIN) themselves. To the bank, the transaction appears completely legitimate.

**NIRNAY** solves this by establishing a **hybrid decision intelligence platform** that operates inside a full neo-banking container. NIRNAY evaluates transactions not as isolated events, but as actions within a behavioral context:
1. **Behavioral Digital Twin**: Analyzes deviation from the user's spending habits (amount, location, device, frequency).
2. **Rule Engine & ML**: Runs deterministic policy rules alongside SHAP feature models.
3. **Multi-Agent Collaborative AI Core**: Invokes 5 specialized LLM agents (Context, Policy, Interpretation, Memory, Conversation) to evaluate intent, scan natural language justifications for scam patterns, and decide the final status (`APPROVED`, `CHALLENGED`, or `BLOCKED`).

---

## 🏗️ Technical Architecture & Transaction Lifecycle

NIRNAY uses a multi-layered security architecture that intercepts transactions at three distinct checkpoints: **Account Integrity (Gateway)**, **Algorithmic Assessment (Risk Engines)**, and **Cognitive Verification (Multi-Agent Reasoning)**.

### Detailed System Flowchart
```mermaid
flowchart TD
    classDef api fill:#6366f1,stroke:#312e81,color:#fff,stroke-width:2px;
    classDef security fill:#ef4444,stroke:#7f1d1d,color:#fff,stroke-width:2px;
    classDef ai fill:#10b981,stroke:#064e3b,color:#fff,stroke-width:2px;
    classDef ledger fill:#f59e0b,stroke:#78350f,color:#fff,stroke-width:2px;

    %% Entrypoints
    Start["Initiate Transfer (P2P / Standard)"]:::api --> CheckFreeze{"Account Frozen Check?"}:::security
    
    %% Gateway Security Checks
    CheckFreeze -- Yes --> BlockFreeze["Reject: Account is Frozen"]:::security
    CheckFreeze -- No --> CheckLimit{"Daily Transfer Limit Check?"}:::security
    
    CheckLimit -- Exceeded --> BlockLimit["Reject: Daily Limit Exceeded"]:::security
    CheckLimit -- Under Limit --> CheckBalance{"Insufficient Balance Check?"}:::security
    
    CheckBalance -- True --> BlockBalance["Reject: Insufficient Funds"]:::security
    CheckBalance -- False --> CheckCooling{"Beneficiary Cooling Check?"}:::security

    %% Cooling Period Logic
    CheckCooling -- Created < 24h & amount > $10,000 --> ApplyCooling["Force OTP + Increase Risk score by +20"]:::security
    CheckCooling -- Safe --> RunEngines["Parallel Evaluation Engines"]:::api

    ApplyCooling --> RunEngines

    %% Algorithmic Assessment
    subgraph Algorithmic Assessment Layer
        RunEngines --> RuleEngine["Deterministic Rule Engine\n(8 compliance policies)"]:::api
        RunEngines --> MLEngine["ML Risk Evaluator\n(Feature weights & SHAP)"]:::api
    end

    RuleEngine --> MultiAgent["Multi-Agent AI Core (LangGraph)"]:::ai
    MLEngine --> MultiAgent

    %% Cognitive Verification
    subgraph Cognitive Verification (LangGraph Collaborative Agents)
        MultiAgent --> ContextAgent["Context Agent\n(Collects History Metadata)"]:::ai
        ContextAgent --> InterpretationAgent["Interpretation Agent\n(Correlates Rules & ML Output)"]:::ai
        InterpretationAgent --> PolicyAgent["Policy Agent\n(Verifies regulatory limits)"]:::ai
        PolicyAgent --> MemoryAgent["Memory Agent\n(Commits profiles to memory)"]:::ai
        PolicyAgent --> ConversationAgent["Conversation Agent\n(Prompts intent confirmation)"]:::ai
    end

    MemoryAgent --> ChallengePath{"Determine Authentication Challenge?"}:::security
    ConversationAgent --> ChallengePath

    %% Adaptive Challenges
    ChallengePath -- Safe (Low Risk) --> ApproveTx["Auto-Approve Transaction"]:::ledger
    ChallengePath -- Challenged (Elevated Risk) --> ShowChallenges["Challenge Screen\n(MPIN / OTP / Intent Justification)"]:::security

    ShowChallenges -- Verification Fails / Scam Flags Triggered --> BlockTx["Block Transaction & Log Threat"]:::security
    ShowChallenges -- Verification Passes --> ApproveTx

    %% Ledger Operations
    ApproveTx --> DeductSender["Deduct Sender Balance"]:::ledger
    DeductSender --> LedgerDebit["Record DEBIT Ledger Entry"]:::ledger
    
    LedgerDebit --> IsP2P{"Is P2P Inter-User Transfer?"}:::ledger
    IsP2P -- Yes --> CreditReceiver["Credit Receiver Balance"]:::ledger
    CreditReceiver --> LedgerCredit["Record CREDIT Ledger Entry"]:::ledger
    
    IsP2P -- No --> Complete["Transaction Complete"]:::ledger
    LedgerCredit --> Complete
```

### Collaborative Multi-Agent Consensus Timeline
Every transaction evaluated by the cognitive layer goes through a consensus trace log that maps exactly how the agents reached a final decision:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Context Agent  │ ➔ ➔   │  Interp Agent   │ ➔ ➔   │  Policy Agent   │ ➔ ➔   │ Decision Engine │
└────────┬────────┘       └────────┬────────┘       └────────┬────────┘       └────────┬────────┘
         │                         │                         │                         │
  Reads customer twin      Correlates ML outputs     Checks daily velocity     Calculates final
  profile, device history  & triggered rule flags    compliance metrics        adaptive Auth requirements
  & trusted beneficiaries  to score anomalies        and fraud threat cards    (Approve/Challenge/Block)
```

---

## 🧠 Deep-Dive Feature Catalog

### AI & Social Engineering Protection Core
*   **LangGraph Collaborative Agents**:
    *   *Context Agent*: Gathers and structure transaction history metadata.
    *   *Interpretation Agent*: Resolves anomalies between ML outputs and rule triggers.
    *   *Policy Agent*: Reviews compliance parameters.
    *   *Conversation Agent*: Prompts the user with natural language questions if intent is ambiguous.
    *   *Memory Agent*: Stores historical transaction logs for future context.
*   **Explainable ML Risk & SHAP values**: Computes risk probability based on features like location match, device integrity, spending velocity, and recipient reputation. Renders interactive horizontal SHAP chart bars to explain decision parameters.
*   **Fallback Heuristics**: If the primary Groq LLM API quota is exhausted or times out, the backend automatically fails-safe to robust local keyword policy scanners (checking 30+ scam terms) to protect users.

### Neo-Banking Operations & Ledger System
*   **Passbook Ledger**: All cash movements are logged inside a database Ledger containing credit/debit types, amount, snapshot balances, and description.
*   **Virtual Card Generator**: Create custom Visa/Mastercard virtual cards with expiry date, CVV, toggleable freeze locks, and customized spending limits.
*   **Term Fixed Deposits (FD)**: Lock funds inside term deposits for scaling annual interest return yields (up to 8.0%). Fully supports premature liquidations with interest penalties.
*   **Personalized Integrity Rewards**: Unlocks cashback offers and discount vouchers (NordVPN, Amazon prime deals) dynamically scaled based on the user's Safety Integrity Score.
*   **Direct P2P Routing**: Send funds instantly to other accounts via a 12-digit account number. Fetches and verifies beneficiary legal name in real-time.
*   **Demo Balance Deposits**: Add mock funds instantly using UPI, Wire Transfer, Salary Credits, or Refund categories.
*   **Statement Exports**: Export full ledger statements in `.csv` format for accounting or reporting.

### Enterprise Security Controls
*   **Brute Force Lockout**: 5 failed login credentials entries locks the account for 15 minutes. Logs events to the security activity audit trail.
*   **Emergency Account Freeze**: User-initiated freeze instantly disables all outgoing transfers. Unfreezable only by inputting the correct 4-6 digit MPIN.
*   **Daily Spending Limits**: Custom daily spending limits validated and confirmed via security MPIN.
*   **Inactivity Session Timeout**: Standard 10-minute inactivity monitor. Prompts a warning alert at the 9-minute mark and auto-logouts the user to prevent screen-takeover threats.

### Unique Strategic Capabilities
*   **Scam Drill Simulator**: 8 interactive gamified training exercises based on real-world Indian scam scripts (phishing emails, KYC updates, police arrest threats, OLX UPI refund requests).
*   **AI Explainability Report**: Downloads a fully structured markdown audit report (`.md`) containing ML models parameters, SHAP variables, triggered policy rules, and multi-agent reasoning timelines for regulatory compliance.
*   **Velocity Heatmap**: Grid maps the frequency and risk of transactions over 7 days and 24 hours.

---

## 🔌 API Endpoints Reference

### Authentication Operations
*   `POST /api/v1/auth/register`: Create a new user with full KYC details (Aadhaar, PAN, DL, phone, address).
*   `POST /api/v1/auth/login`: Authenticate credentials, logs login events, increments brute lockout counters.
*   `GET /api/v1/auth/me`: Fetch authenticated user profile data.
*   `PUT /api/v1/auth/profile`: Update contact details (phone, email, address).
*   `POST /api/v1/auth/tour-complete`: Set onboarding tour state to completed.

### Banking Operations
*   `POST /api/v1/banking/deposit`: Add money to account balance.
*   `GET /api/v1/banking/passbook`: Fetch all credit/debit ledger events.
*   `GET /api/v1/banking/balance`: Fetch balance details, account number, IFSC, and credits/debits totals.
*   `GET /api/v1/banking/lookup`: Lookup local user's legal name by account number.
*   `POST /api/v1/banking/p2p-transfer`: Initiate P2P transfer route.

### Security Operations
*   `POST /api/v1/security/freeze`: Freeze account outgoing transfers.
*   `POST /api/v1/security/unfreeze`: Unfreeze account via MPIN.
*   `GET /api/v1/security/activity-log`: Fetch audit trails of security logs.
*   `PUT /api/v1/security/update-limit`: Modify rolling daily transfer limits.
*   `PUT /api/v1/security/change-password`: Update password (checks current password and validates password strength).

### Interactive Core APIs
*   `POST /api/v1/transactions/initiate`: Evaluate standard transaction requests.
*   `POST /api/v1/transactions/authenticate`: Submit MPIN/OTP challenges.
*   `POST /api/v1/transactions/clarify`: Submit natural language justification text.
*   `GET /api/v1/transactions/{transaction_id}/audit`: Fetch decision consensus trace logs.
*   `GET /api/v1/transactions/{transaction_id}/report`: Fetch full compliance download report data.
*   `GET /api/v1/drills/scenario`: Fetch a random scam simulator training task.
*   `POST /api/v1/drills/answer`: Verify scam simulator answers.

---

## 🗄️ Database Models & Schemas

### User Database Model (`models.py`)
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    balance = Column(Float, default=10000.0)
    security_score = Column(Float, default=85.0)
    mpin = Column(String, nullable=True)
    
    # KYC
    full_name = Column(String)
    phone = Column(String)
    address = Column(Text)
    aadhaar_last4 = Column(String(4))
    pan_number = Column(String(10))
    driving_license = Column(String, nullable=True)
    account_number = Column(String(12), unique=True)
    
    # Safety Locks
    is_frozen = Column(Boolean, default=False)
    daily_transfer_limit = Column(Float, default=200000.0)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
```

---

## ⚙️ Detailed Installation & Setup Guide

### System Prerequisites
- Python 3.9 or higher
- Node.js v16 or higher

### 1. Backend Setup
```bash
# Navigate to the backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run server
python run.py
```
FastAPI server starts on `http://localhost:8000`. Database file `nirnay.db` will be created automatically.

### 2. Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install packages
npm install

# Start Vite dev server
npm run dev
```
Open your browser and navigate to `http://localhost:5173`.

---

## 🧪 Verification & Testing Suite

NIRNAY is built with test-driven integrity. You can verify the behavior of all ML predictions, multi-agent decisions, and core endpoints using the python test suites.

### Run ML Models & Digital Twin Tests
```bash
cd backend
.\venv\Scripts\python test_ml_twin.py
```
*Verifies: ML risk score weighting calculations, SHAP contributions mapping, and Digital Twin parameter updates.*

### Run API Route Integration Tests
```bash
cd backend
.\venv\Scripts\python test_integration.py
```
*Verifies: Account creation KYC parameters parsing, login lockout timers, deposits execution, and P2P payments security evaluation.*

### Run TypeScript Compilation Check
```bash
cd frontend
npx tsc --noEmit
```
*Verifies: Full frontend TypeScript compilation compiles clean.*
