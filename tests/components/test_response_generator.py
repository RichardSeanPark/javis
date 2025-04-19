# tests/components/test_response_generator.py
import pytest
from unittest.mock import patch, AsyncMock
from src.jarvis.components.response_generator import ResponseGenerator

@pytest.fixture
def response_generator():
    """Provides a ResponseGenerator instance for testing."""
    return ResponseGenerator()

# --- Test Cases from markdown/testcase.md Section 6 ---

def test_response_generator_instantiation():
    """6: ResponseGenerator 인스턴스화 테스트"""
    try:
        generator = ResponseGenerator()
        assert isinstance(generator, ResponseGenerator)
    except Exception as e:
        pytest.fail(f"ResponseGenerator instantiation failed: {e}")

@pytest.mark.asyncio
async def test_generate_response_english_input(response_generator):
    """6: generate_response 기본 동작 (영어 입력)"""
    result = "Test result string."
    lang = "en"
    final_response = await response_generator.generate_response(result, lang)
    assert final_response == result

@pytest.mark.asyncio
async def test_generate_response_non_english_placeholder(response_generator):
    """6: generate_response 기본 동작 (비영어 입력, Placeholder)"""
    result = "Test result string."
    lang = "ko"
    final_response = await response_generator.generate_response(result, lang)
    expected_prefix = "(In English, as translation is not yet implemented):"
    assert final_response.startswith(expected_prefix)
    assert result in final_response

@pytest.mark.asyncio
async def test_generate_response_none_input(response_generator):
    """6: generate_response None 입력 처리"""
    lang = "en"
    final_response = await response_generator.generate_response(None, lang)
    assert "I received an empty response" in final_response

@pytest.mark.asyncio
async def test_generate_response_non_string_input(response_generator):
    """6: generate_response 비문자열 입력 처리"""
    result = {"key": "value", "number": 123}
    lang = "en"
    final_response = await response_generator.generate_response(result, lang)
    assert final_response == str(result) # Expect string conversion

@pytest.mark.asyncio
async def test_generate_response_empty_string_input(response_generator):
    """Additional test for empty string input."""
    result = ""
    lang = "en"
    final_response = await response_generator.generate_response(result, lang)
    assert final_response == "" # Empty string should probably remain empty

# TODO: Add tests for actual translation once implemented
# Example structure (requires mocking translate_text):
# @pytest.mark.asyncio
# async def test_generate_response_translation_success(response_generator):
#     with patch('src.jarvis.components.response_generator.translate_text', new_callable=AsyncMock) as mock_translate:
#         mock_translate.return_value = "번역된 결과"
#         result = "Original English Result"
#         lang = "ko"
#         final_response = await response_generator.generate_response(result, lang)
#         mock_translate.assert_called_once_with(text=result, target_language=lang, source_language='en')
#         assert final_response == "번역된 결과"

# @pytest.mark.asyncio
# async def test_generate_response_translation_failure(response_generator):
#     with patch('src.jarvis.components.response_generator.translate_text', new_callable=AsyncMock) as mock_translate:
#         mock_translate.side_effect = Exception("Translation API error")
#         result = "Original English Result"
#         lang = "ko"
#         final_response = await response_generator.generate_response(result, lang)
#         mock_translate.assert_called_once()
#         # Expect fallback to English
#         assert final_response == result 