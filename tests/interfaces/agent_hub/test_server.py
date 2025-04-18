# tests/interfaces/agent_hub/test_server.py
import pytest
from fastapi.testclient import TestClient

# Assuming the server file is correctly placed for this import
from src.jarvis.interfaces.agent_hub.server import app, registered_agents, AgentCard, AgentCapability

@pytest.fixture(scope="function") # Use function scope to reset state between tests
def client():
    """Provides a FastAPI TestClient for the Agent Hub app."""
    # Clear registered agents before each test
    registered_agents.clear()
    with TestClient(app) as c:
        yield c
    # Clear again after test (optional, but good practice)
    registered_agents.clear()

# Sample Agent Card Data for testing
SAMPLE_AGENT_CARD_1 = {
    "agent_id": "agent-coding-001",
    "name": "Test Coding Agent",
    "description": "Generates Python code.",
    "capabilities": [{"name": "code_generation"}, {"name": "python"}]
}

SAMPLE_AGENT_CARD_2 = {
    "agent_id": "agent-qa-002",
    "name": "Test QA Agent",
    "description": "Answers questions.",
    "capabilities": [{"name": "question_answering"}]
}

def test_read_root(client):
    """Test the root health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Jarvis Agent Hub is running."}

def test_register_agent_success(client):
    """Test successful agent registration."""
    response = client.post("/register", json=SAMPLE_AGENT_CARD_1)
    assert response.status_code == 201
    assert response.json() == {"message": f"Agent {SAMPLE_AGENT_CARD_1['name']} registered successfully."}
    # Check if it's actually stored
    assert "agent-coding-001" in registered_agents
    assert registered_agents["agent-coding-001"].name == SAMPLE_AGENT_CARD_1['name']

def test_register_agent_overwrite(client):
    """Test overwriting an existing agent registration."""
    # First registration
    client.post("/register", json=SAMPLE_AGENT_CARD_1)
    # Second registration with the same ID but different name
    updated_card = SAMPLE_AGENT_CARD_1.copy()
    updated_card["name"] = "Updated Coding Agent"
    response = client.post("/register", json=updated_card)
    assert response.status_code == 201 # Still returns 201 on overwrite
    # Check if the agent was updated
    assert "agent-coding-001" in registered_agents
    assert registered_agents["agent-coding-001"].name == "Updated Coding Agent"

def test_list_agents_empty(client):
    """Test listing agents when none are registered."""
    response = client.get("/agents")
    assert response.status_code == 200
    assert response.json() == []

def test_list_agents_multiple(client):
    """Test listing multiple registered agents."""
    client.post("/register", json=SAMPLE_AGENT_CARD_1)
    client.post("/register", json=SAMPLE_AGENT_CARD_2)
    response = client.get("/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 2
    # Check if both agent IDs are present in the response list
    agent_ids = {agent['agent_id'] for agent in agents}
    assert "agent-coding-001" in agent_ids
    assert "agent-qa-002" in agent_ids

def test_discover_agents_empty_request_no_agents(client):
    """Test discovery with no agents registered."""
    discovery_request = {"required_capabilities": []}
    response = client.post("/discover", json=discovery_request)
    assert response.status_code == 200
    assert response.json() == {"discovered_agents": []}

def test_discover_agents_empty_request_with_agents(client):
    """Test discovery (no filter) with registered agents."""
    client.post("/register", json=SAMPLE_AGENT_CARD_1)
    client.post("/register", json=SAMPLE_AGENT_CARD_2)
    discovery_request = {"required_capabilities": []} # Empty capabilities list
    response = client.post("/discover", json=discovery_request)
    assert response.status_code == 200
    discovered = response.json()["discovered_agents"]
    assert len(discovered) == 2 # Placeholder returns all agents
    agent_ids = {agent['agent_id'] for agent in discovered}
    assert "agent-coding-001" in agent_ids
    assert "agent-qa-002" in agent_ids

def test_discover_agents_with_capabilities_placeholder(client):
    """Test discovery with capabilities (placeholder still returns all)."""
    client.post("/register", json=SAMPLE_AGENT_CARD_1)
    client.post("/register", json=SAMPLE_AGENT_CARD_2)
    discovery_request = {
        "required_capabilities": [{"name": "code_generation"}]
    }
    response = client.post("/discover", json=discovery_request)
    assert response.status_code == 200
    discovered = response.json()["discovered_agents"]
    # TODO: Update this test when filtering is implemented.
    # Currently, it should return both agents due to placeholder logic.
    assert len(discovered) == 2
    agent_ids = {agent['agent_id'] for agent in discovered}
    assert "agent-coding-001" in agent_ids
    assert "agent-qa-002" in agent_ids

def test_register_invalid_payload(client):
    """Test registration with invalid data (missing required fields)."""
    invalid_payload = {"agent_id": "bad-agent"} # Missing name, desc, capabilities
    response = client.post("/register", json=invalid_payload)
    assert response.status_code == 422 # Unprocessable Entity

def test_discover_invalid_payload(client):
    """Test discovery with invalid data."""
    invalid_payload = {"capabilities": []} # Incorrect field name
    response = client.post("/discover", json=invalid_payload)
    assert response.status_code == 422 