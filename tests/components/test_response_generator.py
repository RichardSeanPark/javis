# tests/components/test_response_generator.py
import pytest
from unittest.mock import patch, AsyncMock
from src.jarvis.components.response_generator import ResponseGenerator

@pytest.fixture
def response_generator():
    """Provides a ResponseGenerator instance for tests."""
    return ResponseGenerator()

def test_response_generator_initialization(response_generator):
    """Test if ResponseGenerator initializes correctly."""
    assert response_generator is not None
    # Add more checks if __init__ becomes complex, e.g., initializing clients

@pytest.mark.asyncio
async def test_generate_response_english_input(response_generator):
    """Test generating response when original language is English."""
    english_result = "  This is the English result.  "
    formatted = await response_generator.generate_response(english_result, 'en')
    assert formatted == "This is the English result."

@pytest.mark.asyncio
@patch('src.jarvis.components.response_generator.translate_text', new_callable=AsyncMock) # Mock translate_text
async def test_generate_response_translation_needed(mock_translate, response_generator):
    """Test generating response with translation."""
    english_result = "Hello"
    original_language = "ko"
    expected_translation = "안녕하세요"
    mock_translate.return_value = expected_translation

    final_response = await response_generator.generate_response(english_result, original_language)

    mock_translate.assert_awaited_once_with(text="Hello", target_language="ko", source_language='en')
    assert final_response == expected_translation

@pytest.mark.asyncio
@patch('src.jarvis.components.response_generator.translate_text', new_callable=AsyncMock)
async def test_generate_response_translation_error(mock_translate, response_generator):
    """Test fallback to English when translation fails."""
    english_result = "Error case"
    original_language = "ko"
    mock_translate.side_effect = Exception("Translation API failed")

    final_response = await response_generator.generate_response(english_result, original_language)

    mock_translate.assert_awaited_once_with(text="Error case", target_language="ko", source_language='en')
    # Should return the original English result on error
    assert final_response == "Error case"

@pytest.mark.asyncio
async def test_generate_response_non_string_input(response_generator):
    """Test handling of non-string input (dict/list)."""
    dict_result = {"key": "value", "number": 123}
    list_result = [1, "item", True]

    # Test dict
    formatted_dict = await response_generator.generate_response(dict_result, 'en')
    assert formatted_dict == "{'key': 'value', 'number': 123}"

    # Test list
    formatted_list = await response_generator.generate_response(list_result, 'en')
    assert formatted_list == "[1, 'item', True]"

@pytest.mark.asyncio
async def test_generate_response_empty_input(response_generator):
    """Test handling of empty string or None input."""
    empty_string_result = ""
    none_result = None
    expected_default = "I received an empty response."

    formatted_empty = await response_generator.generate_response(empty_string_result, 'en')
    assert formatted_empty == expected_default

    formatted_none = await response_generator.generate_response(none_result, 'en')
    assert formatted_none == expected_default

@pytest.mark.asyncio
@patch('src.jarvis.components.response_generator.translate_text', new_callable=AsyncMock)
async def test_generate_response_empty_input_translation(mock_translate, response_generator):
    """Test that empty input is not translated."""
    empty_string_result = ""
    original_language = "ko"
    expected_default = "I received an empty response."

    final_response = await response_generator.generate_response(empty_string_result, original_language)

    mock_translate.assert_not_awaited() # Translation should not be called
    assert final_response == expected_default 