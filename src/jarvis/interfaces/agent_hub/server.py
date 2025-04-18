# src/jarvis/interfaces/agent_hub/server.py
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# --- Data Models ---
class AgentCapability(BaseModel):
    """Represents a capability required or offered by an agent."""
    name: str = Field(description="Name of the capability, e.g., 'code_generation', 'web_search'.")
    # Add more fields as needed, e.g., input/output schema

class AgentCard(BaseModel):
    """Represents the information card for an agent."""
    agent_id: str = Field(description="Unique identifier for the agent.")
    name: str = Field(description="Human-readable name of the agent.")
    description: str = Field(description="Description of the agent's purpose.")
    capabilities: List[AgentCapability] = Field(description="List of capabilities the agent offers.")
    # Add more fields like endpoint URL, authentication details, cost, etc.

class DiscoveryRequest(BaseModel):
    """Request model for the /discover endpoint."""
    required_capabilities: List[AgentCapability] = Field(description="List of capabilities the requesting agent needs.")
    # Add more filters like preferred_cost, minimum_reliability etc.

class DiscoveryResponse(BaseModel):
    """Response model for the /discover endpoint."""
    discovered_agents: List[AgentCard] = Field(description="List of agents matching the requested capabilities.")

# --- In-Memory Storage (Placeholder) ---
# In a real scenario, use a database or a more robust storage mechanism.
registered_agents: Dict[str, AgentCard] = {}

# --- FastAPI App ---
app = FastAPI(
    title="Jarvis Agent Hub",
    description="A central discovery service for Jarvis-compatible agents (A2A).",
    version="0.1.0",
)

@app.get("/", summary="Health Check")
async def read_root():
    """Basic health check endpoint."""
    logger.info("Agent Hub root endpoint '/' accessed.")
    return {"message": "Jarvis Agent Hub is running."}

@app.post("/discover", response_model=DiscoveryResponse, summary="Discover Agents")
async def discover_agents(request: DiscoveryRequest):
    """
    Discovers agents based on required capabilities.
    (Placeholder implementation - returns all registered agents for now).
    """
    logger.info(f"Received discovery request for capabilities: {request.required_capabilities}")

    # TODO: Implement actual matching logic based on request.required_capabilities
    # For now, return all registered agents as a placeholder.
    matching_agents = list(registered_agents.values())

    logger.info(f"Discovery found {len(matching_agents)} matching agents (placeholder).")
    return DiscoveryResponse(discovered_agents=matching_agents)

@app.post("/register", status_code=201, summary="Register Agent (Placeholder)")
async def register_agent(agent_card: AgentCard):
    """
    Registers an agent with the Hub.
    (Placeholder implementation).
    """
    if agent_card.agent_id in registered_agents:
        logger.warning(f"Agent with ID '{agent_card.agent_id}' is already registered. Overwriting.")
        # raise HTTPException(status_code=409, detail="Agent with this ID already registered.")
    registered_agents[agent_card.agent_id] = agent_card
    logger.info(f"Agent '{agent_card.name}' (ID: {agent_card.agent_id}) registered/updated.")
    return {"message": f"Agent {agent_card.name} registered successfully."}

@app.get("/agents", response_model=List[AgentCard], summary="List Registered Agents")
async def list_agents():
    """Lists all currently registered agents."""
    logger.info(f"Listing all {len(registered_agents)} registered agents.")
    return list(registered_agents.values())

# --- (Optional) Run with Uvicorn for local testing ---
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001) # Use a different port than ADK web 