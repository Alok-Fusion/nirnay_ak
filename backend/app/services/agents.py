from sqlalchemy.orm import Session
from app.models.models import User, DigitalTwin, Recipient, Transaction
import json

class ContextAgent:
    def execute(self, db: Session, user: User, twin: DigitalTwin, recipient: Recipient, amount: float) -> dict:
        log_entry = {
            "agent": "Context Agent",
            "action": "Context Gathering",
            "message": f"Loaded profile for user '{user.username}' (Trust Tier: {twin.trust_level}). "
                       f"Recipient '{recipient.name}' has a trust score of {recipient.trust_score}% "
                       f"and is {'BLACKLISTED' if recipient.is_blacklisted else 'whitelisted'}. "
                       f"Requested transfer: ${amount:,.2f}."
        }
        return log_entry

class InterpretationAgent:
    def execute(self, ml_risk_data: dict) -> dict:
        risk_score = ml_risk_data.get("risk_score", 0.0)
        shap_vals = ml_risk_data.get("shap_values", {})
        
        # Build explanation of SHAP variables
        reasons = []
        for feature, contribution in shap_vals.items():
            if contribution > 15.0:
                reasons.append(f"CRITICAL ANOMALY: '{feature}' contributed heavily (+{contribution}%) to transaction risk.")
            elif contribution > 0.0:
                reasons.append(f"ANOMALY: '{feature}' increased risk score by +{contribution}%.")
            elif contribution < -3.0:
                reasons.append(f"SAFEGUARD: '{feature}' offset risk score by {contribution}%.")
                
        message = f"ML Engine produced a Risk Score of {risk_score}% (Confidence: {ml_risk_data.get('confidence', 0.85)*100}%). "
        if reasons:
            message += "Feature Contributions: " + " | ".join(reasons)
        else:
            message += "All features within typical behavioral thresholds."

        return {
            "agent": "Interpretation Agent",
            "action": "Explainable ML Interpretation",
            "message": message
        }

class PolicyAgent:
    def execute(self, rule_evaluation: dict) -> dict:
        triggered = rule_evaluation.get("triggered_rules", [])
        details = rule_evaluation.get("rule_details", {})
        
        policies = []
        for rule in triggered:
            detail = details.get(rule, {})
            policies.append(f"Triggered Policy '{rule}': {detail.get('desc', '')} (Severity: {detail.get('severity', '')})")
            
        message = f"Policy engine evaluated {len(triggered)} rule violations. "
        if policies:
            message += "Incidents: " + " | ".join(policies)
        else:
            message += "No policy violations. Transaction complies with standard banking guidelines."

        return {
            "agent": "Policy Agent",
            "action": "Compliance check",
            "message": message
        }

class ConversationAgent:
    def execute(self, risk_score: float, triggered_rules: list, recipient_name: str) -> dict:
        # Generates customized clarification dialogues to assess user intent
        question = ""
        requires_interaction = False
        
        if "blacklisted_recipient" in triggered_rules:
            question = f"WARNING: You are transferring funds to a blacklisted account ({recipient_name}). If you were instructed to do this via a phone call, voice message, or remote assistance app, this is highly likely a SCAM. What is the specific reason for this transfer?"
            requires_interaction = True
        elif "crypto_recipient" in triggered_rules:
            question = f"CONFIRM INTENT: Transfers to cryptocurrency exchanges are high-risk. Are you initiating this transfer to {recipient_name} of your own free will, or is someone guide-coaching you over a call?"
            requires_interaction = True
        elif risk_score > 45.0:
            question = f"BEHAVIORAL WARNING: This transaction is unusual. Please explain the purpose of sending ${risk_score * 200:,.0f} to {recipient_name}."
            requires_interaction = True
            
        return {
            "agent": "Conversation Agent",
            "action": "Dynamic Intent Checking",
            "message": question if requires_interaction else "Risk does not justify interactive clarification dialogue.",
            "requires_interaction": requires_interaction,
            "clarification_prompt": question
        }

class MemoryAgent:
    def execute(self, user_id: int, status: str, risk_score: float) -> dict:
        message = f"Committed decision '{status}' with Risk Score {risk_score}% to user cognitive twin history index."
        return {
            "agent": "Memory Agent",
            "action": "Update behavioral index",
            "message": message
        }

class MultiAgentOrchestrator:
    def __init__(self):
        self.context_agent = ContextAgent()
        self.interpretation_agent = InterpretationAgent()
        self.policy_agent = PolicyAgent()
        self.conversation_agent = ConversationAgent()
        self.memory_agent = MemoryAgent()

    def run_agents(
        self,
        db: Session,
        sender_id: int,
        recipient_id: int,
        amount: float,
        device: str,
        location: str,
        ml_risk_data: dict,
        rule_data: dict
    ) -> dict:
        user = db.query(User).filter(User.id == sender_id).first()
        twin = db.query(DigitalTwin).filter(DigitalTwin.user_id == sender_id).first()
        recipient = db.query(Recipient).filter(Recipient.id == recipient_id).first()

        logs = []
        
        # 1. Context Agent
        log_ctx = self.context_agent.execute(db, user, twin, recipient, amount)
        logs.append(log_ctx)
        
        # 2. Interpretation Agent
        log_interp = self.interpretation_agent.execute(ml_risk_data)
        logs.append(log_interp)
        
        # 3. Policy Agent
        log_policy = self.policy_agent.execute(rule_data)
        logs.append(log_policy)
        
        # 4. Conversation Agent
        log_conv = self.conversation_agent.execute(
            ml_risk_data.get("risk_score", 0.0),
            rule_data.get("triggered_rules", []),
            recipient.name
        )
        logs.append(log_conv)
        
        # 5. Memory Agent (preliminary check log)
        log_mem = self.memory_agent.execute(sender_id, "EVALUATION_STAGE", ml_risk_data.get("risk_score", 0.0))
        logs.append(log_mem)
        
        requires_clarification = log_conv["requires_interaction"]
        clarification_prompt = log_conv["clarification_prompt"]

        return {
            "agent_logs": logs,
            "requires_clarification": requires_clarification,
            "clarification_prompt": clarification_prompt
        }
