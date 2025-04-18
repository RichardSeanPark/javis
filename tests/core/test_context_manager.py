# tests/core/test_context_manager.py
import pytest
from collections import deque
from src.jarvis.core.context_manager import ContextManager

@pytest.fixture
def context_manager():
    """Provides a fresh ContextManager instance for each test."""
    return ContextManager()

def test_context_manager_initialization(context_manager):
    """Test if the ContextManager initializes correctly."""
    assert isinstance(context_manager.session_histories, dict)
    # defaultdict behavior check might be complex, just check type
    assert len(context_manager.session_histories) == 0

def test_add_message_single_session(context_manager):
    """Test adding messages to a single session."""
    session_id = "session1"
    context_manager.add_message(session_id, "Hello", "Hi there!", "en")
    context_manager.add_message(session_id, "How are you?", "I'm doing well, thanks!", "en")

    assert session_id in context_manager.session_histories
    history = context_manager.session_histories[session_id]
    assert isinstance(history, deque)
    assert len(history) == 2
    assert history[0] == ("Hello", "Hi there!", "en")
    assert history[1] == ("How are you?", "I'm doing well, thanks!", "en")

def test_add_message_multiple_sessions(context_manager):
    """Test adding messages to multiple sessions independently."""
    session1 = "s1"
    session2 = "s2"
    context_manager.add_message(session1, "User1 Input1", "AI1 Resp1", "en")
    context_manager.add_message(session2, "User2 Input1", "AI2 Resp1", "ko")
    context_manager.add_message(session1, "User1 Input2", "AI1 Resp2", "en")

    assert len(context_manager.session_histories) == 2
    assert len(context_manager.session_histories[session1]) == 2
    assert len(context_manager.session_histories[session2]) == 1
    assert context_manager.session_histories[session1][1] == ("User1 Input2", "AI1 Resp2", "en")
    assert context_manager.session_histories[session2][0] == ("User2 Input1", "AI2 Resp1", "ko")

def test_add_message_no_session_id(context_manager, caplog):
    """Test adding a message without a session ID."""
    context_manager.add_message("", "Input", "Response", "en")
    assert "Cannot add message: session_id is required." in caplog.text
    assert len(context_manager.session_histories) == 0

def test_get_formatted_context_basic(context_manager):
    """Test retrieving formatted context."""
    session_id = "session_ctx"
    context_manager.add_message(session_id, "Q1", "A1", "en")
    context_manager.add_message(session_id, "Q2", "A2", "en")
    context_manager.add_message(session_id, "Q3", "A3", "en")

    formatted = context_manager.get_formatted_context(session_id, max_history=2)
    expected = "User: Q2\nAI: A2\nUser: Q3\nAI: A3"
    assert formatted == expected

def test_get_formatted_context_less_than_max(context_manager):
    """Test retrieving context when history is less than max_history."""
    session_id = "session_less"
    context_manager.add_message(session_id, "Q1", "A1", "en")

    formatted = context_manager.get_formatted_context(session_id, max_history=5)
    expected = "User: Q1\nAI: A1"
    assert formatted == expected

def test_get_formatted_context_empty_history(context_manager):
    """Test retrieving context for a session ID that exists but has no messages (should not happen with defaultdict)."""
    session_id = "session_empty"
    # Accessing the session_id creates the deque via defaultdict
    _ = context_manager.session_histories[session_id]
    formatted = context_manager.get_formatted_context(session_id, max_history=5)
    assert formatted == ""

def test_get_formatted_context_unknown_session(context_manager, caplog):
    """Test retrieving context for an unknown session ID."""
    formatted = context_manager.get_formatted_context("unknown_session", max_history=5)
    assert formatted == ""
    assert "No history found for session_id: unknown_session" in caplog.text

def test_history_max_length(context_manager):
    """Test if the deque correctly enforces maxlen."""
    session_id = "session_maxlen"
    # Get the default maxlen from the specific deque instance
    maxlen = context_manager.session_histories[session_id].maxlen

    for i in range(maxlen + 5): # Add more messages than maxlen
        context_manager.add_message(session_id, f"Q{i}", f"A{i}", "en")

    assert len(context_manager.session_histories[session_id]) == maxlen
    # Check if the first message (Q0) is gone
    first_message_in_deque = context_manager.session_histories[session_id][0]
    assert first_message_in_deque[0] != "Q0"
    # Check if the last message is Q{maxlen+4}
    last_message_in_deque = context_manager.session_histories[session_id][-1]
    assert last_message_in_deque[0] == f"Q{maxlen + 4}"


def test_clear_history_existing(context_manager):
    """Test clearing history for an existing session."""
    session_id = "session_clear"
    context_manager.add_message(session_id, "Q1", "A1", "en")
    assert session_id in context_manager.session_histories

    context_manager.clear_history(session_id)
    assert session_id not in context_manager.session_histories

def test_clear_history_non_existent(context_manager, caplog):
    """Test clearing history for a non-existent session."""
    context_manager.clear_history("non_existent_session")
    assert "Attempted to clear history for non-existent session_id: non_existent_session" in caplog.text
    # Ensure no new entry was created
    assert "non_existent_session" not in context_manager.session_histories 