import os
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import settings
from services.logger import app_logger

class LLMClient:
    """Handles interaction with the Mistral AI model, with fallbacks."""

    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        """Lazily initialize the LLM client to avoid import-time crashes."""
        if self._llm is None:
            api_key = settings.MISTRAL_API_KEY
            if not api_key:
                app_logger.warning("MISTRAL_API_KEY is not set. LLM calls will use fallback mock intelligence.")
                return None
            try:
                self._llm = ChatMistralAI(
                    model="mistral-small-latest",
                    api_key=api_key,
                    temperature=0.2,
                )
            except Exception as e:
                app_logger.error(f"Failed to initialize ChatMistralAI: {e}")
                self._llm = None
        return self._llm

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """
        Generate an LLM response with fallback options.
        """
        model = self.llm
        if model is None:
            return self._generate_fallback(system_prompt, user_prompt)

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            response = model.invoke(messages)
            return response.content
        except Exception as e:
            app_logger.exception(f"LLM generation failed, using fallback: {e}")
            return self._generate_fallback(system_prompt, user_prompt)

    def founder_insight(
        self,
        analytics_summary: dict,
        user_question: str,
        system_prompt: str,
    ) -> str:
        """
        Generate founder-level business insights.
        """
        prompt = f"""
Founder Question:
{user_question}

Business Metrics:
{analytics_summary}

Answer ONLY using the supplied metrics.

Requirements:
- Executive summary
- Mention important numbers
- Mention business risks
- Mention opportunities
- Give practical recommendations
- Keep the response under 250 words.
"""
        return self.generate(system_prompt, prompt)

    def _generate_fallback(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a rule-based mock response if LLM is unavailable."""
        app_logger.info("Generating mock fallback response...")
        
        # Simple heuristic parser for mock responses
        user_prompt_lower = user_prompt.lower()
        
        # Try to parse analytics dictionary from prompt text if present
        import re
        import ast
        
        analytics_summary = {}
        # Find dictionary-like structures
        match = re.search(r"Business Metrics:\s*(\{.*?\})", user_prompt, re.DOTALL)
        if not match:
            # Maybe inside analytics keyword
            match = re.search(r"analytics:\s*(\{.*?\})", user_prompt, re.DOTALL)
            
        if match:
            try:
                analytics_summary = ast.literal_eval(match.group(1).strip())
            except Exception:
                pass

        if not analytics_summary:
            # Fallback values
            analytics_summary = {
                "pipeline_value": 45000000.0,
                "expected_revenue": 18200000.0,
                "average_deal_size": 250000.0,
                "delayed_projects": 3,
                "outstanding_receivables": 12000000.0
            }

        # Check for specific intents
        if "pipeline" in user_prompt_lower:
            val = analytics_summary.get("pipeline_value", 45000000.0)
            exp = analytics_summary.get("expected_revenue", 18200000.0)
            avg = analytics_summary.get("average_deal_size", 250000.0)
            return f"""### 📊 Executive Pipeline Summary (Demo Mode)
- **Total Pipeline Value:** ₹{val:,.2f}
- **Expected Revenue:** ₹{exp:,.2f} (weighted by closure probability)
- **Average Deal Size:** ₹{avg:,.2f}

**Key Business Risks:**
- High concentration of deal values in Negotiation and Proposal stages.
- Several high-value deals have tentative close dates that have passed.

**Opportunities:**
- 3 key deals are in the negotiation stage with probability > 80%; focus on closure this week.
- Solar/Wind sectors show a 25% increase in pipeline velocity.

**Actionable Next Steps:**
1. BD managers should contact stakeholders of the pending qualified deals immediately.
2. Review resource allocations for the upcoming onboarding phase.
"""
        elif "delay" in user_prompt_lower or "work order" in user_prompt_lower or "late" in user_prompt_lower:
            del_proj = analytics_summary.get("delayed_projects", 3)
            rec = analytics_summary.get("outstanding_receivables", 12000000.0)
            return f"""### 🚧 Execution Status & Work Orders (Demo Mode)
- **Delayed Projects:** {del_proj} projects are currently behind schedule.
- **Outstanding Receivables:** ₹{rec:,.2f} remains unbilled or unpaid.

**Key Business Risks:**
- Delayed execution leads to customer dissatisfaction and deferred milestones.
- Outstanding collections affect operational cash flow.

**Opportunities:**
- Standardizing the validation steps for completed work orders will release pending cash milestones.

**Actionable Next Steps:**
1. Escalate delayed work orders SDPLDEAL-075 and SDPLDEAL-102 to the operations head.
2. Re-engage clients with pending receivables to initiate payment cycles.
"""
        else:
            val = analytics_summary.get("pipeline_value", 45000000.0)
            exp = analytics_summary.get("expected_revenue", 18200000.0)
            del_proj = analytics_summary.get("delayed_projects", 3)
            rec = analytics_summary.get("outstanding_receivables", 12000000.0)
            return f"""### 📈 Executive Business Report (Demo Mode)
- **Current Pipeline:** ₹{val:,.2f} across all sales sectors.
- **Expected Revenue:** ₹{exp:,.2f} is projected based on deal closure probabilities.
- **Operational Health:** {del_proj} delayed work orders require immediate attention.
- **Receivables:** ₹{rec:,.2f} is currently outstanding.

**Risks & Caveats:**
- Cash flow is pressured by high outstanding receivables.
- Delay rate on work orders is at 15%, which is above the target of 5%.

**Opportunities & Actions:**
1. Follow up on the ₹{rec:,.2f} receivables to improve liquid cash positions.
2. Resolve scheduling bottlenecks for the delayed projects to meet SLAs.
"""

llm_client = LLMClient()