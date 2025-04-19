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
    result = await web_search(query)

    mock_ddgs_instance.atext.assert_awaited_once_with(query, max_results=5)
    assert "Web Search Results:" in result
    assert "1. Result 1" in result
    assert "URL: http://example.com/1" in result
    assert "Snippet: Snippet 1..." in result
    assert "2. Result 2" in result
    assert "URL: http://example.com/2" in result
    assert "Snippet: Snippet 2..." in result

@pytest.mark.asyncio
@patch('src.jarvis.tools.web_search_tool.DDGS', new_callable=MagicMock)
async def test_web_search_no_results(mock_ddgs_class):
    """웹 검색 결과가 없을 때 적절한 메시지를 반환하는지 테스트합니다."""
    mock_ddgs_instance = AsyncMock()
    mock_ddgs_instance.atext = AsyncMock(return_value=MOCK_EMPTY_RESULTS)
    mock_ddgs_class.return_value.__aenter__.return_value = mock_ddgs_instance

    query = "obscure query"
    result = await web_search(query)

    mock_ddgs_instance.atext.assert_awaited_once_with(query, max_results=5)
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

    mock_ddgs_instance.atext.assert_awaited_once_with(query, max_results=5)
    assert "An error occurred while searching the web: API connection failed" in result

# TODO: Add test for registration in tools/__init__.py after implementing that step

def test_web_search_tool_registration():
    """웹 검색 도구가 tools/__init__.py의 available_tools 리스트에 등록되었는지 확인합니다."""
    from src.jarvis.tools import available_tools, web_search_tool
    assert web_search_tool in available_tools 