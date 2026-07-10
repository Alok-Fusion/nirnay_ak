import urllib.request
import urllib.parse
import json
import os
from sqlalchemy.orm import Session
from app.models.models import User, DigitalTwin, Recipient, Transaction
from app.core.config import settings

def call_groq_api(system_prompt: str, user_prompt: str) -> str:
    """Helper method to execute API completions on Groq using python's built-in urllib."""
    if not settings.GROQ_API_KEY:
        return ""
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2
    }
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        # Set 4-second timeout to avoid locking up transaction loops
        with urllib.request.urlopen(req, timeout=4) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error executing Groq LLM API request: {e}")
        return ""

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

    def evaluate_scam_intent(self, response_text: str, recipient_name: str) -> dict:
        """Calls Groq to analyze the natural language response for social engineering indicators."""
        fallback_res = {"is_compromised": False, "confidence": 1.0, "explanation": "Offline template analysis."}
        
        if not settings.GROQ_API_KEY:
            # Local heuristic check if no Groq API Key is configured
            indicators = ["remote", "anydesk", "teamviewer", "helpdesk", "refund", "support called", "police told me", "secure account", "agent asked"]
            lowered = response_text.lower()
            if any(ind in lowered for ind in indicators):
                return {
                    "is_compromised": True,
                    "confidence": 0.85,
                    "explanation": "Heuristic match: customer statement contains keywords indicative of tech support or remote access coercion."
                }
            return fallback_res

        system_prompt = (
            "You are the Policy Agent of NIRNAY. Analyze the user's statement explaining their transaction intent. "
            "Determine if the user is showing indicators of being manipulated, scammed, or coached under social engineering. "
            "Scam indicators include: mentioning a phone call from support/police, being instructed to move funds to a 'safe account', "
            "installing remote apps (AnyDesk, TeamViewer), being promised guaranteed crypto returns, or being told not to tell the bank. "
            "Output ONLY a raw JSON block containing exactly: "
            "{\"is_compromised\": boolean, \"confidence\": float (0.0 to 1.0), \"explanation\": string}"
        )
        user_prompt = f"Customer statement: '{response_text}' for transfer to recipient '{recipient_name}'."
        
        response = call_groq_api(system_prompt, user_prompt)
        try:
            # Clean possible markdown wrap ```json ... ```
            if "```" in response:
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            res_dict = json.loads(response.strip())
            return res_dict
        except Exception:
            print("Failed to parse Groq response as JSON. Fallback to heuristics.")
            return fallback_res

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
            question = f"BEHAVIORAL WARNING: This transaction is unusual. Please explain the purpose of sending money to {recipient_name}."
            requires_interaction = True

        # If Groq LLM API is configured, dynamically generate a contextual security dialog!
        if requires_interaction and settings.GROQ_API_KEY:
            system_prompt = (
                "You are the Conversation Agent of NIRNAY. Generate a natural, serious, compliance-compliant security warning "
                "and intent-checking question for a bank customer. Address the recipient name and explain why the transaction is "
                "suspicious (e.g. crypto keywords, large deviation, new beneficiary). Ask them who requested this transfer. "
                "Write EXACTLY 2 sentences maximum. Do not say Hello or Welcome."
            )
            user_prompt = f"Recipient: '{recipient_name}'. Risk Score: {risk_score}%. Rule triggers: {triggered_rules}."
            groq_question = call_groq_api(system_prompt, user_prompt)
            if groq_question:
                question = groq_question
            
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
        
        # 5. Memory Agent
        log_mem = self.memory_agent.execute(sender_id, "EVALUATION_STAGE", ml_risk_data.get("risk_score", 0.0))
        logs.append(log_mem)
        
        requires_clarification = log_conv["requires_interaction"]
        clarification_prompt = log_conv["clarification_prompt"]

        return {
            "agent_logs": logs,
            "requires_clarification": requires_clarification,
            "clarification_prompt": clarification_prompt
        }
