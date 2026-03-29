from agents.portfolio_agent import PortfolioAgent
from agents.radar_agent import RadarAgent
from agents.chart_agent import ChartAgent

class OrchestratorAgent:
    """
    Master Orchestrator Agent.
    Receives user intent and routes to the correct specialized agent.
    Coordinates all agents and combines results.
    """

    def __init__(self):
        self.portfolio_agent = PortfolioAgent()
        self.radar_agent = RadarAgent()
        self.chart_agent = ChartAgent()
        self.agent_log = []

    def log(self, message):
        self.agent_log.append(message)

    def route(self, intent: str, data=None):
        """
        Routes request to correct agent based on intent.
        intents: 'portfolio', 'radar', 'chart'
        """
        self.agent_log = []
        self.log(f"[Orchestrator] Received intent: {intent}")

        if intent == "portfolio":
            self.log("[Orchestrator] Routing to Portfolio Agent")
            result = self.portfolio_agent.run(data)
            self.log("[Orchestrator] Portfolio Agent completed")
            return result

        elif intent == "radar":
            self.log("[Orchestrator] Routing to Radar Agent")
            result = self.radar_agent.run(data)
            self.log("[Orchestrator] Radar Agent completed")
            return result

        elif intent == "chart":
            self.log("[Orchestrator] Routing to Chart Agent")
            result = self.chart_agent.run(data)
            self.log("[Orchestrator] Chart Agent completed")
            return result

        else:
            self.log(f"[Orchestrator] Unknown intent: {intent}")
            return {"error": f"Unknown intent: {intent}"}

    def get_log(self):
        return self.agent_log