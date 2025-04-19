"""Tests for the integration between JarvisDispatcher and ResponseGenerator."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.jarvis.core.dispatcher import JarvisDispatcher
from src.jarvis.components.response_generator import ResponseGenerator
from src.jarvis.models.input import ParsedInput # For mocking parser result
from google.genai.types import GenerateContentResponse # For mocking LLM response
from google.adk.agents import BaseAgent as Agent
from google.adk.events import Event # <<< Import Event
from google.genai.types import Content, Part # <<< Import Content, Part
import httpx # <<< Import httpx for mocking A2A errors
# Import actual tools for verification
from src.jarvis.tools import code_execution_tool, web_search_tool, translate_tool

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

# --- Test Cases from markdown/testcase.md Section 3.6 (Error Handling) ---

@pytest.mark.asyncio
async def test_error_input_parsing(mock_dispatcher_with_mock_resp_gen):
    """3.6: 입력 파싱 오류 테스트 (Mock)"""
    dispatcher, _, mock_input_parser, _ = mock_dispatcher_with_mock_resp_gen
    mock_input_parser.process_input.side_effect = Exception("Parsing failed!")

    result = await dispatcher.process_request("some input", session_id="test-session")
    assert result == "Error: Failed to parse your input."

@pytest.mark.asyncio
async def test_error_llm_delegation(mock_dispatcher_with_mock_resp_gen):
    """3.6: LLM 위임 결정 오류 테스트 (Mock)"""
    dispatcher, _, mock_input_parser, mock_llm_client = mock_dispatcher_with_mock_resp_gen

    # Setup mock parsed input
    mock_parsed = ParsedInput(original_text="q", original_language="en", english_text="query")
    mock_input_parser.process_input.return_value = mock_parsed

    # Simulate LLM error
    mock_llm_client.aio.models.generate_content.side_effect = Exception("LLM API Error")

    result = await dispatcher.process_request("some input", session_id="test-session")
    # Expect fallback to "no suitable agent" message as LLM error leads to NO_AGENT internal state
    assert result == "I cannot find a suitable agent to handle your request at this time."

@pytest.mark.asyncio
async def test_error_a2a_discovery(mock_dispatcher_with_mock_resp_gen):
    """3.6: A2A 검색 오류 테스트 (Mock)"""
    dispatcher, _, mock_input_parser, mock_llm_client = mock_dispatcher_with_mock_resp_gen

    mock_parsed = ParsedInput(original_text="q", original_language="en", english_text="query", intent="a2a_needed", domain="unknown")
    mock_input_parser.process_input.return_value = mock_parsed

    # Mock LLM to return NO_AGENT to trigger A2A check
    mock_response = MagicMock(spec=GenerateContentResponse)
    mock_response.text = "NO_AGENT"
    mock_llm_client.aio.models.generate_content.return_value = mock_response

    # Simulate A2A discovery error
    dispatcher._discover_a2a_agents.side_effect = httpx.RequestError("Connection failed")

    result = await dispatcher.process_request("some input", session_id="test-session")
    # A2A discovery error should lead to fallback message
    assert result == "I cannot find a suitable agent to handle your request at this time."
    dispatcher._call_a2a_agent.assert_not_called() # Ensure call wasn't attempted

@pytest.mark.asyncio
async def test_error_a2a_call(mock_dispatcher_with_mock_resp_gen):
    """3.6: A2A 호출 오류 테스트 (Mock)"""
    dispatcher, _, mock_input_parser, mock_llm_client = mock_dispatcher_with_mock_resp_gen

    mock_parsed = ParsedInput(original_text="q", original_language="en", english_text="query", intent="a2a_needed", domain="unknown")
    mock_input_parser.process_input.return_value = mock_parsed

    mock_response = MagicMock(spec=GenerateContentResponse)
    mock_response.text = "NO_AGENT"
    mock_llm_client.aio.models.generate_content.return_value = mock_response

    # Mock successful discovery
    mock_agent_card = {"name": "A2A_Agent", "a2a_endpoint": "http://a2a.test"}
    dispatcher._discover_a2a_agents.return_value = [mock_agent_card]

    # Simulate A2A call error
    dispatcher._call_a2a_agent.side_effect = Exception("A2A Call Failed")

    result = await dispatcher.process_request("some input", session_id="test-session")
    # A2A call error is now caught within process_request, should return fallback
    assert result == "I cannot find a suitable agent to handle your request at this time."
    dispatcher._call_a2a_agent.assert_called_once_with(mock_agent_card, mock_parsed.english_text)

@pytest.mark.asyncio
async def test_error_sub_agent_access(mock_dispatcher_with_mock_resp_gen):
    """3.6: 하위 에이전트 접근 오류 테스트 (Mock)"""
    dispatcher, mock_response_gen, mock_input_parser, _ = mock_dispatcher_with_mock_resp_gen

    invalid_agent_name = "NonExistentAgent"
    delegation_info = {
        "agent_name": invalid_agent_name,
        "input_text": "test input",
        "original_language": "en",
        "required_tools": [],
        "conversation_history": None
    }

    # Mock process_request to return info for an invalid agent
    with patch('src.jarvis.core.dispatcher.JarvisDispatcher.process_request',
               new_callable=AsyncMock, return_value=delegation_info):

        dispatcher.current_original_language = "en" # Set language for ResponseGenerator
        mock_ctx = MagicMock()
        mock_ctx.user_content.parts[0].text = "some query"
        mock_session = MagicMock(); mock_session.id = "error-session"
        mock_ctx.session = mock_session

        final_event = None
        async for event in dispatcher._run_async_impl(mock_ctx):
            final_event = event

        assert final_event is not None
        expected_error_msg = f"Error: Could not find agent {invalid_agent_name} to delegate to."
        # Check that ResponseGenerator was called with the specific error
        mock_response_gen.generate_response.assert_called_once_with(expected_error_msg, "en")
        # Check the final event content (processed by the mock ResponseGenerator)
        assert final_event.content.parts[0].text == f"Processed: {expected_error_msg} (Lang: en)"

@pytest.mark.asyncio
async def test_error_response_generator(mock_dispatcher_with_mock_resp_gen):
    """3.6: 응답 생성기 오류 테스트 (Mock)"""
    dispatcher, mock_response_gen, _, _ = mock_dispatcher_with_mock_resp_gen

    # Simulate an error during response generation
    mock_response_gen.generate_response.side_effect = Exception("Generator failed!")

    # Trigger a scenario where ResponseGenerator is called (e.g., direct response)
    direct_response = "Some direct message"
    with patch('src.jarvis.core.dispatcher.JarvisDispatcher.process_request',
               new_callable=AsyncMock, return_value=direct_response):

        dispatcher.current_original_language = "fr"
        mock_ctx = MagicMock()
        mock_ctx.user_content.parts[0].text = "some query"
        mock_session = MagicMock(); mock_session.id = "gen-error-session"
        mock_ctx.session = mock_session

        final_event = None
        async for event in dispatcher._run_async_impl(mock_ctx):
            final_event = event

        assert final_event is not None
        # Check that the raw fallback error message is in the event
        assert final_event.content.parts[0].text == "Error: Failed to generate final response."
        # Verify ResponseGenerator was called (even though it failed)
        mock_response_gen.generate_response.assert_called_once_with(direct_response, "fr")

@pytest.mark.asyncio
async def test_error_process_request_unexpected(mock_dispatcher_with_mock_resp_gen):
    """3.6: process_request 전체 오류 테스트 (Mock)"""
    dispatcher, _, mock_input_parser, _ = mock_dispatcher_with_mock_resp_gen

    # Mock a step inside process_request (e.g., prompt building) to raise an unexpected error
    with patch('src.jarvis.core.dispatcher.JarvisDispatcher.get_llm_client') as mock_get_client:
         # Mock input parser to return something valid initially
         mock_parsed = ParsedInput(original_text="q", original_language="en", english_text="query")
         mock_input_parser.process_input.return_value = mock_parsed
         # Make get_llm_client raise an error *before* the LLM call
         mock_get_client.side_effect = Exception("Unexpected internal error!")

         result = await dispatcher.process_request("some input", session_id="test-session")
         assert result == "Error: An unexpected internal error occurred while processing your request."

@pytest.mark.asyncio
async def test_error_run_async_impl_unexpected(mock_dispatcher_with_mock_resp_gen):
    """3.6: _run_async_impl 전체 오류 테스트 (Mock)"""
    dispatcher, mock_response_gen, _, _ = mock_dispatcher_with_mock_resp_gen

    # Mock process_request itself to raise an unexpected error
    # Use patch to mock the method on the class level to avoid Pydantic validation error
    with patch.object(JarvisDispatcher, 'process_request', new_callable=AsyncMock) as mock_process_req:
        mock_process_req.side_effect = Exception("Run impl unexpected error!")

        dispatcher.current_original_language = "es"
        mock_ctx = MagicMock()
        mock_ctx.user_content.parts[0].text = "some query"
        mock_session = MagicMock(); mock_session.id = "run-impl-error-session"
        mock_ctx.session = mock_session

        final_event = None
        async for event in dispatcher._run_async_impl(mock_ctx):
            final_event = event

        assert final_event is not None
        expected_error_msg = "Error: An unexpected error occurred."
        # Check ResponseGenerator was called with the default fallback message
        mock_response_gen.generate_response.assert_called_once_with(expected_error_msg, "es")
        # Check the final event content (processed by the mock ResponseGenerator)
        assert final_event.content.parts[0].text == f"Processed: {expected_error_msg} (Lang: es)"

# --- Test Case from markdown/testcase.md Section 5.5 (Tool Injection Logic) ---

@pytest.mark.asyncio
async def test_process_request_includes_correct_tools(mock_dispatcher_with_mock_resp_gen):
    """5.5: process_request가 agent_tool_map 기반 올바른 툴 목록을 DelegationInfo에 포함하는지 확인"""
    dispatcher, _, mock_input_parser, mock_llm_client = mock_dispatcher_with_mock_resp_gen

    # -- Scenario 1: Delegate to CodingAgent --
    agent_to_select = "CodingAgent"
    expected_tools = dispatcher.agent_tool_map[agent_to_select]
    expected_tool_names = sorted([tool.name for tool in expected_tools if hasattr(tool, 'name')])

    # Mock input parsing result
    mock_parsed = ParsedInput(original_text="code q", original_language="en", english_text="code query")
    mock_input_parser.process_input.return_value = mock_parsed

    # Mock LLM decision to select CodingAgent
    mock_response_coding = MagicMock(spec=GenerateContentResponse)
    mock_response_coding.text = agent_to_select
    mock_llm_client.aio.models.generate_content.return_value = mock_response_coding

    # Call process_request
    result_coding = await dispatcher.process_request("code query", session_id="tool-test-session-1")

    # Assertions for CodingAgent
    assert isinstance(result_coding, dict)
    assert result_coding.get("agent_name") == agent_to_select
    assert "required_tools" in result_coding
    # Extract names carefully, considering tools might not have .name directly
    actual_tool_names_coding = sorted([
        tool.name if hasattr(tool, 'name') 
        else tool.function_declarations[0].name if hasattr(tool, 'function_declarations') and tool.function_declarations 
        else 'UnknownTool' 
        for tool in result_coding["required_tools"]
    ])
    assert actual_tool_names_coding == expected_tool_names
    assert code_execution_tool.name in actual_tool_names_coding # Explicit check

    # -- Scenario 2: Delegate to KnowledgeQA_Agent --
    agent_to_select_qa = "KnowledgeQA_Agent"
    # Debug: Print the agent_tool_map content for QA agent
    # print(f"\nDEBUG: agent_tool_map for {agent_to_select_qa}: {[getattr(t, 'name', 'N/A') for t in dispatcher.agent_tool_map.get(agent_to_select_qa, [])]}") # Removed debug print
    expected_tools_qa = dispatcher.agent_tool_map[agent_to_select_qa]
    # Expected names should include function names for tools without direct .name
    expected_tool_names_qa = sorted([
        tool.name if hasattr(tool, 'name') 
        else tool.function_declarations[0].name if hasattr(tool, 'function_declarations') and tool.function_declarations 
        else 'UnknownTool' 
        for tool in expected_tools_qa
    ])

    # Mock input parsing result (can reuse or create new)
    mock_parsed_qa = ParsedInput(original_text="qa q", original_language="ko", english_text="qa query")
    mock_input_parser.process_input.return_value = mock_parsed_qa # Update mock return value

    # Mock LLM decision to select KnowledgeQA_Agent
    mock_response_qa = MagicMock(spec=GenerateContentResponse)
    mock_response_qa.text = agent_to_select_qa
    # Reset the mock return value for the new scenario
    mock_llm_client.aio.models.generate_content.return_value = mock_response_qa

    # Call process_request again
    result_qa = await dispatcher.process_request("qa query", session_id="tool-test-session-2")

    # Assertions for KnowledgeQA_Agent
    assert isinstance(result_qa, dict)
    assert result_qa.get("agent_name") == agent_to_select_qa
    assert "required_tools" in result_qa
    # Extract names carefully, considering tools might not have .name directly
    actual_tool_names_qa = sorted([
        tool.name if hasattr(tool, 'name') 
        else tool.function_declarations[0].name if hasattr(tool, 'function_declarations') and tool.function_declarations 
        else 'UnknownTool' 
        for tool in result_qa["required_tools"]
    ])
    assert actual_tool_names_qa == expected_tool_names_qa
    # Check for tool presence using the extracted names list
    assert web_search_tool.name in actual_tool_names_qa # Check by name
    assert "translate_text" in actual_tool_names_qa # Check by function name 