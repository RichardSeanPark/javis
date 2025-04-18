# tests/interfaces/a2a_adapter/test_adk_agent_a2a_server.py
import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio # Ensure asyncio is imported for potential use in mocks/tests

# Import necessary classes from your project
from google.adk import agents as adk_agents
from src.jarvis.libs.a2a import models as a2a_models
from src.jarvis.interfaces.a2a_adapter.adk_agent_a2a_server import AdkAgentA2AWrapper

# --- Test Fixtures ---

@pytest.fixture
def mock_adk_agent_sync():
    """Provides a mock synchronous ADK Agent."""
    agent = MagicMock(spec=adk_agents.Agent)
    agent.name = "MockSyncADKAgent"
    # Make __call__ a MagicMock so we can assert calls
    agent.__call__ = MagicMock(return_value="Sync response from ADK Agent")
    # Explicitly mark it as not async - use inspect in the wrapper instead
    # agent.__call__._is_coroutine = False
    return agent

@pytest.fixture
def mock_adk_agent_async():
    """Provides a mock asynchronous ADK Agent."""
    # Create agent as AsyncMock directly, remove spec for now
    agent = AsyncMock() # Removed spec=adk_agents.Agent
    agent.name = "MockAsyncADKAgent"
    # Configure the mock's return value directly - moved to tests where needed
    # agent.return_value = "Async response from ADK Agent"
    return agent

@pytest.fixture
def sample_agent_card():
    """Provides a sample AgentCard for testing."""
    return a2a_models.AgentCard(
        name="Test ADK Agent (A2A)",
        description="An ADK agent wrapped for A2A.",
        version="1.0.0",
        url="http://localhost:9999/a2a",
        authentication=a2a_models.AgentAuthentication(schemes=["none"]),
        capabilities=a2a_models.AgentCapabilities(streaming=False, pushNotifications=False),
        skills=[
            a2a_models.AgentSkill(
                id="textProcessing",
                name="textProcessing",
                description="Handles basic text processing tasks."
            )
        ]
    )

@pytest.fixture
def sample_a2a_task_text_input():
    """Provides a sample A2A Task with simple text input in history."""
    task_id = str(uuid.uuid4())
    initial_message = a2a_models.Message(
        message_id=str(uuid.uuid4()),
        conversation_id=str(uuid.uuid4()),
        role="user",
        parts=[a2a_models.TextPart(text="Hello ADK Agent!")]
    )
    return a2a_models.Task(
        id=task_id,
        # Pass the initial message in the history list
        history=[initial_message],
        status=a2a_models.TaskStatus(state=a2a_models.TaskState.SUBMITTED)
    )

# --- Wrapper Initialization Tests ---

def test_wrapper_init_success(mock_adk_agent_sync, sample_agent_card):
    """Tests successful initialization of the wrapper."""
    wrapper = AdkAgentA2AWrapper(adk_agent=mock_adk_agent_sync, agent_card=sample_agent_card)
    assert wrapper.adk_agent == mock_adk_agent_sync
    assert wrapper.agent_card == sample_agent_card

def test_wrapper_init_invalid_agent_type(sample_agent_card):
    """Tests initialization failure with a non-ADK agent object."""
    invalid_agent = object()
    with pytest.raises(TypeError, match="Provided agent must be an instance of google.adk.agents.Agent"):
        AdkAgentA2AWrapper(adk_agent=invalid_agent, agent_card=sample_agent_card)

# --- handle_task Method Tests ---

@pytest.mark.asyncio
async def test_handle_task_sync_agent_success(mock_adk_agent_sync, sample_agent_card, sample_a2a_task_text_input):
    """Tests handle_task with a synchronous ADK agent succeeding."""
    wrapper = AdkAgentA2AWrapper(adk_agent=mock_adk_agent_sync, agent_card=sample_agent_card)
    # Access input text from history
    input_text = sample_a2a_task_text_input.history[0].parts[0].text
    expected_response = "Sync response from ADK Agent"
    # Ensure the sync mock's __call__ returns the value
    mock_adk_agent_sync.__call__.return_value = expected_response

    # Patch asyncio.to_thread as the wrapper should now use it for sync agents
    # We mock to_thread to check it's called, but make it *actually* run the sync function
    # to ensure the flow inside handle_task works correctly.
    # The original mock_adk_agent_sync.__call__ will be executed by to_thread.
    with patch('src.jarvis.interfaces.a2a_adapter.adk_agent_a2a_server.asyncio.to_thread', wraps=asyncio.to_thread) as mock_to_thread:
        result_task = await wrapper.handle_task(sample_a2a_task_text_input)

        # Check if asyncio.to_thread was awaited with the correct arguments (__call__ method)
        mock_to_thread.assert_awaited_once_with(mock_adk_agent_sync.__call__, input_text)
        # Ensure the original sync mock's __call__ was called (by to_thread)
        mock_adk_agent_sync.__call__.assert_called_once_with(input_text)

        assert result_task.status.state == a2a_models.TaskState.COMPLETED
        assert result_task.artifacts is not None
        assert len(result_task.artifacts) == 1
        assert isinstance(result_task.artifacts[0].parts[0], a2a_models.TextPart)
        assert result_task.artifacts[0].parts[0].text == expected_response

@pytest.mark.asyncio
async def test_handle_task_async_agent_success(mock_adk_agent_async, sample_agent_card, sample_a2a_task_text_input):
    """Tests handle_task with an asynchronous ADK agent succeeding."""
    wrapper = AdkAgentA2AWrapper(adk_agent=mock_adk_agent_async, agent_card=sample_agent_card)
    # Access input text from history
    input_text = sample_a2a_task_text_input.history[0].parts[0].text
    expected_response = "Async response from ADK Agent"
    # Set return_value directly on the AsyncMock instance
    mock_adk_agent_async.return_value = expected_response

    result_task = await wrapper.handle_task(sample_a2a_task_text_input)

    # Assert await directly on the mock instance
    mock_adk_agent_async.assert_awaited_once_with(input_text)
    assert result_task.status.state == a2a_models.TaskState.COMPLETED
    assert result_task.artifacts is not None
    assert len(result_task.artifacts) == 1
    assert isinstance(result_task.artifacts[0].parts[0], a2a_models.TextPart)
    assert result_task.artifacts[0].parts[0].text == expected_response

@pytest.mark.asyncio
async def test_handle_task_agent_exception(mock_adk_agent_async, sample_agent_card, sample_a2a_task_text_input):
    """Tests handle_task when the ADK agent raises an exception."""
    error_message = "ADK agent failed!"
    # Set side_effect directly on the AsyncMock instance
    mock_adk_agent_async.side_effect = Exception(error_message)
    wrapper = AdkAgentA2AWrapper(adk_agent=mock_adk_agent_async, agent_card=sample_agent_card)

    # Pass the task with history to handle_task
    result_task = await wrapper.handle_task(sample_a2a_task_text_input)

    # Assert await directly on the mock instance
    mock_adk_agent_async.assert_awaited_once()
    assert result_task.status.state == a2a_models.TaskState.FAILED
    # Check if artifacts is an empty list or None based on implementation
    assert result_task.artifacts == [] # Assuming it defaults to empty list on error path
    # Verify error is NOT set on task.status anymore
    assert not hasattr(result_task.status, 'error') or result_task.status.error is None

@pytest.mark.asyncio
async def test_handle_task_no_text_part(mock_adk_agent_async, sample_agent_card):
    """Tests handle_task when the input message has no TextPart."""
    task_id = str(uuid.uuid4())
    # Create task with history containing a message without TextPart
    message_no_text = a2a_models.Message(
        message_id=str(uuid.uuid4()),
        conversation_id=str(uuid.uuid4()),
        role="user",
        parts=[a2a_models.DataPart(data={"some": "data"})]
    )
    task_no_text = a2a_models.Task(
        id=task_id,
        history=[message_no_text],
        status=a2a_models.TaskStatus(state=a2a_models.TaskState.SUBMITTED)
    )
    wrapper = AdkAgentA2AWrapper(adk_agent=mock_adk_agent_async, agent_card=sample_agent_card)

    # Expect the agent to be called with empty string
    expected_response = "Async response from ADK Agent"
    # Set return_value directly on the AsyncMock instance
    mock_adk_agent_async.return_value = expected_response

    with patch('src.jarvis.interfaces.a2a_adapter.adk_agent_a2a_server.logger.warning') as mock_log_warning:
        # Pass the modified task
        result_task = await wrapper.handle_task(task_no_text)
        # Check log message based on updated wrapper logic
        mock_log_warning.assert_called_with(f"Task {task_id}: First message has no TextPart.")

    # Assert await directly on the mock instance
    mock_adk_agent_async.assert_awaited_once_with("") # Called with empty string
    assert result_task.status.state == a2a_models.TaskState.COMPLETED
    assert result_task.artifacts[0].parts[0].text == expected_response

@pytest.mark.asyncio
async def test_handle_task_no_message(mock_adk_agent_async, sample_agent_card):
    """Tests handle_task when the input task has no history."""
    task_id = str(uuid.uuid4())
    # Create task with empty history or None
    task_no_history = a2a_models.Task(
        id=task_id,
        history=[], # or history=None depending on how you want to test
        status=a2a_models.TaskStatus(state=a2a_models.TaskState.SUBMITTED)
    )
    wrapper = AdkAgentA2AWrapper(adk_agent=mock_adk_agent_async, agent_card=sample_agent_card)

    expected_response = "Async response from ADK Agent"
    # Set return_value directly on the AsyncMock instance
    mock_adk_agent_async.return_value = expected_response

    with patch('src.jarvis.interfaces.a2a_adapter.adk_agent_a2a_server.logger.warning') as mock_log_warning:
        # Pass the modified task
        result_task = await wrapper.handle_task(task_no_history)
        # Check log message based on updated wrapper logic
        mock_log_warning.assert_called_with(f"Task {task_id} received with no history or parts in the first message.")

    # Assert await directly on the mock instance
    mock_adk_agent_async.assert_awaited_once_with("") # Called with empty string
    assert result_task.status.state == a2a_models.TaskState.COMPLETED
    assert result_task.artifacts[0].parts[0].text == expected_response


# --- TODO: Add tests for FastAPI integration once implemented ---
# These would require setting up a TestClient and mocking the A2AServer's
# interaction with FastAPI or using the actual FastAPI integration if provided
# by the base A2AServer class from src/jarvis/libs/a2a/server/server.py. 