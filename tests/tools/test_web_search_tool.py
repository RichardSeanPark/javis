# tests/tools/test_web_search_tool.py
import pytest
import logging
from unittest.mock import patch, AsyncMock, MagicMock

from src.jarvis.tools.web_search_tool import web_search, web_search_tool
from google.adk.tools import FunctionTool
# Import types needed for schema verification
from google.genai.types import FunctionDeclaration, Schema as GenaiSchema, Type as GenaiType, Tool

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

# Mock data for AsyncDDGS
MOCK_SEARCH_RESULTS = [
    {'title': 'Result 1', 'href': 'http://example.com/1', 'body': 'Snippet 1...'},
    {'title': 'Result 2', 'href': 'http://example.com/2', 'body': 'Snippet 2...'},
]

MOCK_EMPTY_RESULTS = []

# Mock results from DDGS().atext
MOCK_SEARCH_RESULTS_LONG = [
    {'title': 'Async Programming in Python', 'href': 'http://example.com/async', 'body': 'Asyncio provides infrastructure for writing single-threaded concurrent code... It is used for network servers, database connections, and distributed task queues.' * 5}, # Make it long
    {'title': 'Benefits of Async IO', 'href': 'http://example.com/benefits', 'body': 'The main benefit is improved performance for I/O-bound tasks. By yielding control when waiting for I/O, the event loop can run other tasks.' * 5}, # Make it long
]

MOCK_SEARCH_RESULTS_SHORT = [
    {'title': 'DuckDuckGo Search Library', 'href': 'http://example.com/ddgs', 'body': 'A simple library to use DuckDuckGo search.'},
]

# Mock LLM response
MOCK_LLM_SUMMARY = "Async programming in Python, using asyncio, improves performance for I/O-bound tasks like networking by allowing concurrent execution without threads."

def test_web_search_tool_definition():
    """웹 검색 도구(web_search_tool) 객체가 올바르게 정의되었는지 확인합니다."""
    # Check against the specific ADK FunctionTool type
    assert isinstance(web_search_tool, FunctionTool)
    # Check the name derived from the function
    assert web_search_tool.name == "web_search"
    # Check that the description exists (derived from docstring)
    assert web_search_tool.description is not None and len(web_search_tool.description) > 0

    # Note: Accessing detailed parameter schema (types, required) from FunctionTool
    # object can be unreliable or depend on internal ADK details.
    # We rely on the function signature and other tests for functional verification.

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS', new_callable=MagicMock)
async def test_web_search_success(mock_ddgs_class):
    """웹 검색이 성공하고 결과가 올바르게 포맷되는지 테스트합니다."""
    # Configure the mock AsyncDDGS instance and its methods
    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_SEARCH_RESULTS_SHORT)
    mock_ddgs_class.return_value.__aenter__.return_value = mock_ddgs_instance

    query = "test query"
    result = await web_search(query)

    mock_ddgs_instance.atext.assert_awaited_once_with(query, max_results=7)
    assert "Web Search Results for 'test query':" in result
    assert "1. DuckDuckGo Search Library" in result
    assert "URL: http://example.com/ddgs" in result
    assert "Snippet: A simple library to use DuckDuckGo search." in result

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS', new_callable=MagicMock)
async def test_web_search_no_results(mock_ddgs_class):
    """웹 검색 결과가 없을 때 적절한 메시지를 반환하는지 테스트합니다."""
    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_EMPTY_RESULTS)
    mock_ddgs_class.return_value.__aenter__.return_value = mock_ddgs_instance

    query = "obscure query"
    result = await web_search(query)

    mock_ddgs_instance.atext.assert_awaited_once_with(query, max_results=7)
    assert result == "No relevant information found on the web for your query."

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS', new_callable=MagicMock)
async def test_web_search_api_error(mock_ddgs_class):
    """웹 검색 중 API 오류가 발생했을 때 에러 메시지를 반환하는지 테스트합니다."""
    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext = AsyncMock(side_effect=Exception("API connection failed"))
    mock_ddgs_class.return_value.__aenter__.return_value = mock_ddgs_instance

    query = "error query"
    result = await web_search(query)

    mock_ddgs_instance.atext.assert_awaited_once_with(query, max_results=7)
    assert "An error occurred while searching the web: API connection failed" in result

# TODO: Add test for registration in tools/__init__.py after implementing that step

def test_web_search_tool_registration():
    """웹 검색 도구가 tools/__init__.py의 available_tools 리스트에 등록되었는지 확인합니다."""
    from src.jarvis.tools import available_tools, web_search_tool
    assert web_search_tool in available_tools 

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS')
@patch('src.jarvis.tools.web_search_tool.genai.GenerativeModel')
@patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', True) # Assume LLM is initialized
async def test_web_search_summary_success(mock_genai_model, mock_ddgs):
    """5.3: 요약 성공 테스트 (Mock LLM)"""
    # Mock DDGS().atext behavior
    mock_ddgs_instance = mock_ddgs.return_value.__aenter__.return_value
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_SEARCH_RESULTS_LONG)

    # Mock GenerativeModel behavior
    mock_model_instance = mock_genai_model.return_value
    mock_llm_response = MagicMock()
    mock_llm_response.text = MOCK_LLM_SUMMARY
    mock_model_instance.generate_content_async = AsyncMock(return_value=mock_llm_response)

    query = "benefits of async programming"
    result = await web_search(query)

    # Assertions
    mock_ddgs_instance.atext.assert_called_once_with(query, max_results=7)
    mock_genai_model.assert_called_once() # Check model was instantiated
    mock_model_instance.generate_content_async.assert_called_once() # Check LLM was called
    # Check if the correct prompt structure was passed (simplified check)
    call_args, _ = mock_model_instance.generate_content_async.call_args
    assert f"query '{query}'" in call_args[0]
    assert "Search Results Snippets:" in call_args[0]
    assert MOCK_SEARCH_RESULTS_LONG[0]['body'] in call_args[0] # Check if content is in prompt

    assert f"Summary based on web search results for '{query}':" in result
    assert MOCK_LLM_SUMMARY in result


@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS')
@patch('src.jarvis.tools.web_search_tool.genai.GenerativeModel')
@patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', True) # Assume LLM is initialized
async def test_web_search_summary_skipped_short_results(mock_genai_model, mock_ddgs):
    """5.3: 요약 건너뛰기 테스트 (짧은 결과)"""
    # Mock DDGS().atext behavior
    mock_ddgs_instance = mock_ddgs.return_value.__aenter__.return_value
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_SEARCH_RESULTS_SHORT)

    # Mock GenerativeModel (though it shouldn't be called)
    mock_model_instance = mock_genai_model.return_value
    mock_model_instance.generate_content_async = AsyncMock()

    query = "ddgs library"
    result = await web_search(query)

    # Assertions
    mock_ddgs_instance.atext.assert_called_once_with(query, max_results=7)
    mock_genai_model.assert_not_called() # Check model was NOT instantiated
    mock_model_instance.generate_content_async.assert_not_called() # Check LLM was NOT called

    assert "Web Search Results for" in result
    assert "(Note: Summarization failed" not in result # Ensure no failure note
    assert MOCK_SEARCH_RESULTS_SHORT[0]['title'] in result # Check raw results are present


@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS')
@patch('src.jarvis.tools.web_search_tool.genai.GenerativeModel')
@patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', False) # *** Mock LLM as NOT initialized ***
async def test_web_search_summary_skipped_llm_not_initialized(mock_genai_model, mock_ddgs):
    """5.3: 요약 건너뛰기 테스트 (LLM 미초기화)"""
    # Mock DDGS().atext behavior (use long results to ensure length isn't the skip reason)
    mock_ddgs_instance = mock_ddgs.return_value.__aenter__.return_value
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_SEARCH_RESULTS_LONG)

    # Mock GenerativeModel (though it shouldn't be called)
    mock_model_instance = mock_genai_model.return_value
    mock_model_instance.generate_content_async = AsyncMock()

    query = "long query but no llm"
    result = await web_search(query)

    # Assertions
    mock_ddgs_instance.atext.assert_called_once_with(query, max_results=7)
    mock_genai_model.assert_not_called() # Check model was NOT instantiated
    mock_model_instance.generate_content_async.assert_not_called() # Check LLM was NOT called

    assert "Web Search Results for" in result
    assert "(Note: Summarization failed" not in result # Ensure no failure note
    assert MOCK_SEARCH_RESULTS_LONG[0]['title'] in result # Check raw results are present


@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS')
@patch('src.jarvis.tools.web_search_tool.genai.GenerativeModel')
@patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', True) # Assume LLM is initialized
async def test_web_search_summary_failure_llm_error(mock_genai_model, mock_ddgs):
    """5.3: 요약 실패 테스트 (Mock LLM 에러)"""
    # Mock DDGS().atext behavior
    mock_ddgs_instance = mock_ddgs.return_value.__aenter__.return_value
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_SEARCH_RESULTS_LONG)

    # Mock GenerativeModel to raise an error
    mock_model_instance = mock_genai_model.return_value
    mock_model_instance.generate_content_async = AsyncMock(side_effect=Exception("LLM API Error!"))

    query = "summarization error test"
    result = await web_search(query)

    # Assertions
    mock_ddgs_instance.atext.assert_called_once_with(query, max_results=7)
    mock_genai_model.assert_called_once() # Model was instantiated
    mock_model_instance.generate_content_async.assert_called_once() # LLM call was attempted

    assert "Web Search Results for" in result
    assert "(Note: Summarization failed, showing raw results)" in result # Check for failure note
    assert MOCK_SEARCH_RESULTS_LONG[0]['title'] in result # Check raw results are present 