import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, AsyncMock, patch
from typing import Optional, Union, AsyncGenerator

from google.genai.types import Content, Part
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext

# Import the class to be tested and its dependencies
from src.jarvis.core.dispatcher import JarvisDispatcher, DelegationInfo
from src.jarvis.components.response_generator import ResponseGenerator
from src.jarvis.core.context_manager import ContextManager # Import ContextManager
import logging

logger = logging.getLogger(__name__)

# Test Dispatcher class without modifying its __init__ for this test
class TestDispatcherBase(JarvisDispatcher):
    """Base test dispatcher, mocks process_request."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Replace response_generator with a simple pass-through mock
        mock_response_generator = MagicMock(spec=ResponseGenerator)
        mock_response_generator.generate_response = AsyncMock(side_effect=lambda text, lang: text)
        self.response_generator = mock_response_generator
        self._mock_process_request_return = None

    async def process_request(self, user_input: str, session_id: Optional[str] = None) -> Union[DelegationInfo, str]:
        return self._mock_process_request_return


# Test Suite
class TestDispatcherContextSaving:

    @pytest.fixture
    def test_dispatcher(self):
        """Provides a TestDispatcherBase instance with mocked ContextManager."""
        # Patch genai and httpx as they are used in the original __init__
        with patch('src.jarvis.core.dispatcher.genai'), \
             patch('src.jarvis.core.dispatcher.httpx'):
            # Create the dispatcher instance first
            dispatcher = TestDispatcherBase()

            # Now, mock the context_manager instance specifically for testing add_message
            mock_cm = MagicMock(spec=ContextManager)
            mock_cm.add_message = MagicMock()
            # Replace the actual context_manager instance with the mock
            dispatcher.context_manager = mock_cm

            return dispatcher

    @pytest.fixture
    def mock_invocation_context(self):
        """Provides a mock InvocationContext."""
        ctx = MagicMock(spec=InvocationContext)
        ctx.session = MagicMock()
        ctx.session.id = "test-session-123"
        # Make user_input accessible easily in tests
        ctx.user_input = "Hello Jarvis"
        ctx.user_content = Content(parts=[Part(text=ctx.user_input)])
        return ctx

    @pytest.mark.asyncio
    async def test_context_saved_on_success(self, test_dispatcher, mock_invocation_context):
        """Tests if context is saved when _run_async_impl generates a direct response successfully."""
        user_input = mock_invocation_context.user_input
        ai_response = "Hello User" # This is what process_request returns directly
        original_lang = "en"

        # Configure mocks
        test_dispatcher._mock_process_request_return = ai_response # Simulate direct response
        # Simulate setting language which normally happens in process_request
        test_dispatcher.current_original_language = original_lang

        # Run the implementation
        generator = test_dispatcher._run_async_impl(mock_invocation_context)
        events = [event async for event in generator]

        # Assertions
        assert len(events) == 1 # Should yield one final event
        assert events[0].content.parts[0].text == ai_response

        # Verify context_manager.add_message was called correctly
        test_dispatcher.context_manager.add_message.assert_called_once_with(
            session_id=mock_invocation_context.session.id,
            user_input=user_input,
            ai_response=ai_response, # Should save the final AI response text
            original_language=original_lang
        )

    @pytest.mark.asyncio
    async def test_context_save_failure_logged(self, test_dispatcher, mock_invocation_context, caplog):
        """Tests if an error during context saving is logged but doesn't stop response."""
        user_input = mock_invocation_context.user_input
        ai_response = "Logging test"
        original_lang = "en"

        # Configure mocks
        test_dispatcher._mock_process_request_return = ai_response
        test_dispatcher.current_original_language = original_lang
        # Make add_message raise an error
        test_dispatcher.context_manager.add_message.side_effect = Exception("DB connection failed")

        # Run the implementation
        generator = test_dispatcher._run_async_impl(mock_invocation_context)
        events = [event async for event in generator]

        # Assertions
        assert len(events) == 1 # Should still yield the final event
        assert events[0].content.parts[0].text == ai_response
        # Verify add_message was called
        test_dispatcher.context_manager.add_message.assert_called_once()
        # Check logs for the error
        assert "Failed to save context" in caplog.text
        assert "DB connection failed" in caplog.text

    @pytest.mark.asyncio
    async def test_context_saved_on_generation_error(self, test_dispatcher, mock_invocation_context, caplog):
        """Tests if context (with error message) is saved when response generation fails."""
        user_input = mock_invocation_context.user_input
        error_response = "Error: Failed to generate final response." # Default error in dispatcher
        original_lang = "fr"

        # Configure mocks
        test_dispatcher._mock_process_request_return = "This should fail to generate" # Input to response_generator
        test_dispatcher.current_original_language = original_lang
        # Patch the specific instance's generate_response to raise an error
        test_dispatcher.response_generator.generate_response = AsyncMock(side_effect=Exception("Simulated generation error"))

        # Run the implementation
        generator = test_dispatcher._run_async_impl(mock_invocation_context)
        events = [event async for event in generator]

        # Assertions
        assert len(events) == 1 # Should yield one fallback error event
        assert events[0].content.parts[0].text == error_response # Check the yielded error response

        # Verify add_message was called with the error response
        test_dispatcher.context_manager.add_message.assert_called_once_with(
            session_id=mock_invocation_context.session.id,
            user_input=user_input,
            ai_response=error_response, # Important: The error message should be saved
            original_language=original_lang
        )
        # Check logs for the generation error
        assert "Error during final response generation" in caplog.text
        assert "Simulated generation error" in caplog.text 