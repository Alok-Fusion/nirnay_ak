# NIRNAY: AI-Powered Financial Decision Intelligence Platform

> **Tagline:** Beyond Fraud Detection. Towards Intelligent Financial Decisions.

NIRNAY is an enterprise-grade AI-powered Financial Decision Intelligence Platform that transforms how digital banking transactions are evaluated, secured, and authorized. 

Unlike traditional fraud systems that provide binary outcomes (approve or block), NIRNAY evaluates customer context, validates recipient risk profiles, checks behavioral digital twin deviations, applies banking policy guidelines, runs multi-agent AI reasoning, and triggers adaptive authentication before executing any transaction.

---

## High-Level Architecture Flow

```
Customer → Initiate Transfer → TransactionOrchestrator
                                      │
       ┌──────────────────────────────┴──────────────────────────────┐
       ▼                                                             ▼
Deterministic Rules (rule_engine.py)                 Explainable ML Risk (ml_engine.py)
       │                                                             │
       └──────────────────────────────┬──────────────────────────────┘
                                      ▼
                        LangGraph-style Multi-Agent Core
                                      │
                     ┌────────────────┴────────────────┐
                     ▼                                 ▼
              Decision Engine                 Adaptive Authentication
              (APPROVE / BLOCK / CHALLENGE)   (Password -> MPIN -> OTP)
                                      │
                                      ▼
                             Execution & Audit Log
```

---

## Core Technical Features

1. **Transaction Orchestrator**: Coordinates session checking, balance checks, ML scoring, compliance checking, and agent calls.
2. **Customer Digital Twin**: Dynamically models individual spending velocities, amounts, devices, times, and trusted recipients.
3. **Machine Learning & SHAP Layer**: Predicts risk probability and displays feature-level reason codes.
4. **LangGraph Multi-Agent Core**: 5 collaborative agents (Context, Interpretation, Policy, Conversation, Memory).
5. **Adaptive Authentication**: Seamlessly increases authentication hurdles (MPIN, OTP) as calculated transaction risk increases.
6. **Executive Dashboard**: Dark-themed, responsive portal offering spend charts, trust analysis, admin controls, and transaction timelines.

---

## Project Structure

- `backend/`: FastAPI implementation, SQLite db, SQLAlchemy models, Rule engine, ML engine, and Multi-Agent Orchestrator.
- `frontend/`: React + Vite + TS client interface, dashboard, security center, analytics, admin portal, and orchestrator animation panels.

---

## Setup & Running Instructions

### Backend
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - On Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - On Windows (CMD):
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the development server:
   ```bash
   python run.py
   ```
   The backend API will run on `http://localhost:8000`.

### Frontend
1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite dev server:
   ```bash
   npm run dev
   ```
   The UI will be accessible at `http://localhost:5173`.
