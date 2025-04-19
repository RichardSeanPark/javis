"""Tests for the integration between JarvisDispatcher and ResponseGenerator."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.jarvis.core.dispatcher import JarvisDispatcher
from src.jarvis.components.response_generator import ResponseGenerator
from src.jarvis.models.input import ParsedInput # For mocking parser result
from google.genai.types import GenerateContentResponse # For mocking LLM response
from google.adk.agents import BaseAgent as Agent

@pytest.fixture
def mock_dispatcher_with_mock_resp_gen(mocker):
    """Provides a JarvisDispatcher instance with a mocked ResponseGenerator."""
    # Mock dependencies needed for Dispatcher instantiation if they perform checks
    mocker.patch('src.jarvis.core.dispatcher.InputParserAgent', return_value=MagicMock())
    mocker.patch('src.jarvis.core.dispatcher.JarvisDispatcher._initialize_llm_client', return_value=None)
    mocker.patch('src.jarvis.core.dispatcher.httpx.AsyncClient', return_value=MagicMock())

    # Create Mock Agent instances with name attribute and correct spec
    mock_coding_agent = MagicMock(spec=Agent)
    mock_coding_agent.name = "CodingAgent"
    # Optionally mock other attributes if register_agent uses them (e.g., model)
    # mock_coding_agent.model = "mock-model"

    mock_qa_agent = MagicMock(spec=Agent)
    mock_qa_agent.name = "KnowledgeQA_Agent"
    # mock_qa_agent.model = "mock-model"

    # Patch the classes to return these specific mocks
    mocker.patch('src.jarvis.core.dispatcher.CodingAgent', return_value=mock_coding_agent)
    mocker.patch('src.jarvis.core.dispatcher.KnowledgeQA_Agent', return_value=mock_qa_agent)

    # Create dispatcher instance - now register_agent should work
    dispatcher = JarvisDispatcher()

    # Mock the response_generator instance *after* dispatcher initialization
    mock_response_gen = AsyncMock(spec=ResponseGenerator)
    # Configure its behavior using return_value or side_effect on the AsyncMock itself
    async def mock_generate_side_effect(result, lang):
        return f"Processed: {result} (Lang: {lang})"
    mock_response_gen.generate_response.side_effect = mock_generate_side_effect
    # mock_response_gen.generate_response = mock_generate # Don't assign the function directly

    dispatcher.response_generator = mock_response_gen

    # Mock the input parser behavior for the test
    mock_input_parser = AsyncMock()
    dispatcher.input_parser = mock_input_parser

    # Mock the LLM client behavior for the test
    mock_llm_client = AsyncMock()
    dispatcher.llm_clients[dispatcher.model] = mock_llm_client # Ensure the correct model key is used

    # Mock A2A methods as they might be called
    dispatcher._discover_a2a_agents = AsyncMock(return_value=[])
    dispatcher._call_a2a_agent = AsyncMock()

    return dispatcher, mock_response_gen, mock_input_parser, mock_llm_client

# --- Test Case from markdown/testcase.md Section 6 ---

@pytest.mark.asyncio
async def test_dispatcher_calls_response_generator_on_direct_response(
    mock_dispatcher_with_mock_resp_gen
):
    """6: Dispatcher -> ResponseGenerator 호출 테스트 (Mock)
       Tests if _run_async_impl calls response_generator when process_request returns a string.
    """
    dispatcher, mock_response_gen, mock_input_parser, mock_llm_client = mock_dispatcher_with_mock_resp_gen

    # Scenario 1: process_request returns a non-delegation string (e.g., A2A fail)
    direct_response_string = "I cannot find a suitable agent to handle your request at this time."
    original_lang = "ko"

    # Mock process_request to return the direct string
    # Patch the class method as done previously
    with patch('src.jarvis.core.dispatcher.JarvisDispatcher.process_request',
               new_callable=AsyncMock, return_value=direct_response_string) as mock_process_req:

        # Set the original language that process_request would have set
        dispatcher.current_original_language = original_lang

        # Mock the invocation context passed to _run_async_impl
        mock_ctx = MagicMock()
        mock_ctx.user_content.parts[0].text = "some query" # Ensure user_input is not None
        mock_session = MagicMock(); mock_session.id = "resp-test-session"
        mock_ctx.session = mock_session

        # Consume the generator returned by _run_async_impl
        final_event = None
        async for event in dispatcher._run_async_impl(mock_ctx):
            final_event = event # Capture the last (and only) event expected

        # Assert process_request was called (implicitly by patch)
        mock_process_req.assert_called_once()

        # Assert response_generator.generate_response was called correctly
        mock_response_gen.generate_response.assert_called_once_with(
            direct_response_string, original_lang
        )

        # Assert the final event contains the processed response
        assert final_event is not None
        assert final_event.content.parts[0].text == f"Processed: {direct_response_string} (Lang: {original_lang})" 