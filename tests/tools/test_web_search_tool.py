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
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_SEARCH_RESULTS)
    mock_ddgs_class.return_value.__aenter__.return_value = mock_ddgs_instance

    query = "test query"
    # Patch LLM initialization for this specific test to avoid calling it
    with patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', False):
        result = await web_search(query)

    # Corrected assertion for max_results
    mock_ddgs_instance.atext.assert_awaited_once_with(query, max_results=7)
    # Assertions remain the same for content - summary should NOT be present
    assert "Web Search Results for 'test query':\n\n" in result # Raw results expected
    assert "1. Result 1" in result
    assert "URL: http://example.com/1" in result
    assert "Snippet: Snippet 1..." in result
    assert "Summary based on" not in result

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS', new_callable=MagicMock)
async def test_web_search_no_results(mock_ddgs_class):
    """웹 검색 결과가 없을 때 적절한 메시지를 반환하는지 테스트합니다."""
    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_EMPTY_RESULTS)
    mock_ddgs_class.return_value.__aenter__.return_value = mock_ddgs_instance

    query = "obscure query"
    with patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', False):
        result = await web_search(query)

    # Corrected assertion for max_results
    mock_ddgs_instance.atext.assert_awaited_once_with(query, max_results=7)
    assert result == "No relevant information found on the web for your query."

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS', new_callable=MagicMock)
async def test_web_search_api_error(mock_ddgs_class):
    """웹 검색 중 API 오류가 발생했을 때 에러 메시지를 반환하는지 테스트합니다."""
    mock_ddgs_instance = AsyncMock()
    error_message = "API connection failed"
    mock_ddgs_instance.atext = AsyncMock(side_effect=Exception(error_message))
    mock_ddgs_class.return_value.__aenter__.return_value = mock_ddgs_instance

    query = "error query"
    with patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', False):
        result = await web_search(query)

    # Corrected assertion for max_results
    mock_ddgs_instance.atext.assert_awaited_once_with(query, max_results=7)
    assert f"An error occurred while searching the web: {error_message}" == result

# TODO: Add test for registration in tools/__init__.py after implementing that step

def test_web_search_tool_registration():
    """웹 검색 도구가 tools/__init__.py의 available_tools 리스트에 등록되었는지 확인합니다."""
    from src.jarvis.tools import available_tools, web_search_tool
    assert web_search_tool in available_tools 

"""Tests for the web_search tool, including summarization logic."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
# Import the function to test
from src.jarvis.tools.web_search_tool import web_search

# --- Mock Data ---

# Mock search results from DDGS().atext
# Long results (enough for summarization)
MOCK_SEARCH_RESULTS_LONG = [
    {
        'title': 'Async Programming in Python: The Complete Guide',
        'href': 'http://example.com/async-guide',
        'body': "Asynchronous programming allows... enabling concurrency without threads... greatly improves performance for I/O bound tasks. Python's asyncio library provides..." * 3 # Make it longer than 200 chars
    },
    {
        'title': 'Benefits of Asyncio',
        'href': 'http://example.com/async-benefits',
        'body': "Key benefits include efficient handling of thousands of connections, better resource utilization, and responsive applications. Useful for web servers, database queries..." * 3
    },
]

# Short results (should skip summarization)
MOCK_SEARCH_RESULTS_SHORT = [
    {
        'title': 'duckduckgo_search PyPI',
        'href': 'http://pypi.org/project/duckduckgo_search',
        'body': 'Official PyPI page for the duckduckgo_search library.'
    },
]

# Mock LLM response
MOCK_LLM_SUMMARY = "Async programming in Python, using libraries like asyncio, significantly boosts performance for I/O-bound operations by handling concurrency efficiently without threads, leading to better resource use and responsiveness."

# --- Test Functions ---

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS')
@patch('src.jarvis.tools.web_search_tool.genai.GenerativeModel')
@patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', True) # Assume LLM is initialized
async def test_web_search_summarization_success(mock_genai_model, mock_ddgs):
    """5.3: 요약 성공 테스트 (Mock LLM)"""
    # --- Arrange Mocks ---
    # Mock DDGS response (long results)
    mock_ddgs_instance = mock_ddgs.return_value.__aenter__.return_value
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_SEARCH_RESULTS_LONG)

    # Mock LLM response
    mock_model_instance = mock_genai_model.return_value
    mock_llm_response = MagicMock()
    mock_llm_response.text = MOCK_LLM_SUMMARY
    mock_model_instance.generate_content_async = AsyncMock(return_value=mock_llm_response)
    
    # Explicitly patch DEFAULT_MODEL_NAME for consistency in test assertion
    with patch('src.jarvis.tools.web_search_tool.DEFAULT_MODEL_NAME', 'gemini-2.0-flash'):
        # --- Act ---
        query = "benefits of async programming"
        result = await web_search(query)

    # --- Assert ---
    # DDGS called correctly
    mock_ddgs_instance.atext.assert_called_once_with(query, max_results=7)
    # LLM Model initialized and called with the updated default name
    mock_genai_model.assert_called_once_with('gemini-2.0-flash')
    mock_model_instance.generate_content_async.assert_called_once()
    # Check if the prompt passed to LLM contains expected parts
    call_args, _ = mock_model_instance.generate_content_async.call_args
    prompt_arg = call_args[0]
    assert f"query '{query}'" in prompt_arg
    assert "Title: Async Programming in Python" in prompt_arg # Check content from results
    # Result is the summary
    assert f"Summary based on web search results for '{query}':" in result
    assert MOCK_LLM_SUMMARY in result

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS')
@patch('src.jarvis.tools.web_search_tool.genai.GenerativeModel')
@patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', True)
async def test_web_search_summarization_skipped_short_results(mock_genai_model, mock_ddgs):
    """5.3: 요약 건너뛰기 테스트 (짧은 결과)"""
    # --- Arrange Mocks ---
    # Mock DDGS response (short results)
    mock_ddgs_instance = mock_ddgs.return_value.__aenter__.return_value
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_SEARCH_RESULTS_SHORT)

    # Mock LLM (to ensure it's NOT called)
    mock_model_instance = mock_genai_model.return_value
    mock_model_instance.generate_content_async = AsyncMock()

    # --- Act ---
    query = "pypi duckduckgo_search"
    result = await web_search(query)

    # --- Assert ---
    # DDGS called
    mock_ddgs_instance.atext.assert_called_once_with(query, max_results=7)
    # LLM NOT called
    mock_genai_model.assert_not_called()
    mock_model_instance.generate_content_async.assert_not_called()
    # Result contains raw results format
    assert f"Web Search Results for '{query}'" in result
    assert "duckduckgo_search PyPI" in result # Check content from results
    assert "Summary based on" not in result

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS')
@patch('src.jarvis.tools.web_search_tool.genai.GenerativeModel')
@patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', False) # <<< LLM not initialized
async def test_web_search_summarization_skipped_llm_not_initialized(mock_genai_model, mock_ddgs):
    """5.3: 요약 건너뛰기 테스트 (LLM 미초기화)"""
    # --- Arrange Mocks ---
    # Mock DDGS response (long results, but shouldn't matter)
    mock_ddgs_instance = mock_ddgs.return_value.__aenter__.return_value
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_SEARCH_RESULTS_LONG)

    # Mock LLM (to ensure it's NOT called)
    mock_model_instance = mock_genai_model.return_value
    mock_model_instance.generate_content_async = AsyncMock()

    # --- Act ---
    query = "benefits of async programming"
    result = await web_search(query)

    # --- Assert ---
    # DDGS called
    mock_ddgs_instance.atext.assert_called_once_with(query, max_results=7)
    # LLM NOT called
    mock_genai_model.assert_not_called()
    mock_model_instance.generate_content_async.assert_not_called()
    # Result contains raw results format
    assert f"Web Search Results for '{query}'" in result
    assert "Async Programming in Python" in result # Check content from results
    assert "Summary based on" not in result

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS')
@patch('src.jarvis.tools.web_search_tool.genai.GenerativeModel')
@patch('src.jarvis.tools.web_search_tool.LLM_CLIENT_INITIALIZED', True)
async def test_web_search_summarization_failure_llm_error(mock_genai_model, mock_ddgs):
    """5.3: 요약 실패 테스트 (Mock LLM 에러)"""
    # --- Arrange Mocks ---
    # Mock DDGS response (long results)
    mock_ddgs_instance = mock_ddgs.return_value.__aenter__.return_value
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_SEARCH_RESULTS_LONG)

    # Mock LLM to raise an error
    mock_model_instance = mock_genai_model.return_value
    mock_model_instance.generate_content_async = AsyncMock(side_effect=Exception("LLM API Error!"))

    # --- Act ---
    query = "benefits of async programming"
    result = await web_search(query)

    # --- Assert ---
    # DDGS called
    mock_ddgs_instance.atext.assert_called_once_with(query, max_results=7)
    # LLM Model initialized and called (even though it failed)
    mock_genai_model.assert_called_once()
    mock_model_instance.generate_content_async.assert_called_once()
    # Result contains raw results format AND the failure note
    assert f"Web Search Results for '{query}'" in result
    assert "(Note: Summarization failed, showing raw results)" in result
    assert "Async Programming in Python" in result # Check content from results
    assert "Summary based on" not in result # Summary itself should not be present

# TODO: Add tests for the base web_search functionality (no results, search error)
# These might already exist if there was a previous test file, otherwise add them.

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS')
async def test_web_search_no_results(mock_ddgs):
    """Test web_search when DDGS returns no results."""
    # Arrange
    mock_ddgs_instance = mock_ddgs.return_value.__aenter__.return_value
    mock_ddgs_instance.atext = AsyncMock(return_value=[]) # Empty list

    # Act
    query = "aquerywithnoresultsguaranteed123"
    result = await web_search(query)

    # Assert
    mock_ddgs_instance.atext.assert_called_once_with(query, max_results=7)
    assert result == "No relevant information found on the web for your query."

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS')
async def test_web_search_ddgs_error(mock_ddgs):
    """Test web_search when DDGS().atext raises an exception."""
    # Arrange
    mock_ddgs_instance = mock_ddgs.return_value.__aenter__.return_value
    error_message = "DDGS Search Failed"
    mock_ddgs_instance.atext = AsyncMock(side_effect=Exception(error_message))

    # Act
    query = "test query"
    result = await web_search(query)

    # Assert
    mock_ddgs_instance.atext.assert_called_once_with(query, max_results=7)
    # Corrected assertion using f-string properly
    assert f"An error occurred while searching the web: {error_message}" == result 