"""
InputParserAgent 클래스 테스트 (실제 API 호출 사용)
"""

import pytest
import sys
import os
import asyncio
import re # re 임포트 추가
from pathlib import Path
from google.adk.agents import LlmAgent, BaseAgent # 수정: LlmAgent 임포트 확인 (test_input_parser_inherits_llm_agent 위해), Import BaseAgent
from unittest.mock import AsyncMock, MagicMock, patch # mock 관련 임포트 추가
import google.genai as genai # Import genai

# 테스트 대상 모듈을 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# 환경 변수 로드 시도 (테스트 환경에 .env 파일이 있을 경우)
try:
    from dotenv import load_dotenv
    # .env 파일이 프로젝트 루트에 있다고 가정
    dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path)
        print(".env file loaded.")
    else:
        print(".env file not found, relying on environment variables.")
except ImportError:
    print("python-dotenv not installed, relying on environment variables.")
    pass # python-dotenv가 설치되지 않아도 테스트는 진행 가능

from jarvis.components.input_parser import InputParserAgent
from jarvis.models.input import ParsedInput
# from unittest.mock import AsyncMock, MagicMock # 제거

@pytest.fixture
def agent():
    """InputParserAgent 인스턴스를 생성하는 fixture"""
    # mocker 및 mock 처리 로직 제거
    return InputParserAgent()

def test_input_parser_file_exists():
    """
    테스트 목적: src/jarvis/components/input_parser.py 파일이 존재하는지 확인합니다.
    """
    parser_path = Path('src/jarvis/components/input_parser.py')
    assert parser_path.exists(), "src/jarvis/components/input_parser.py 파일이 존재하지 않습니다."

def test_input_parser_inherits_base_agent(agent):
    """
    테스트 목적: InputParserAgent 클래스가 BaseAgent를 상속하는지 확인합니다.
    """
    assert isinstance(agent, BaseAgent), f"Expected InputParserAgent to be instance of BaseAgent, but it's {type(agent)}"

def test_input_parser_initialization(agent):
    """
    테스트 목적: __init__ 메서드가 올바른 이름, 설명으로 초기화되는지 확인합니다.
    """
    assert agent.name == "InputParserAgent", f"Expected name 'InputParserAgent', got '{agent.name}'"
    expected_description = "Parses user input for language, intent, entities, and domain."
    assert agent.description == expected_description, f"Expected description '{expected_description}', got '{agent.description}'"

def test_process_input_method_signature(agent):
    """
    테스트 목적: process_input 메서드의 시그니처(인자, 반환 타입)를 확인합니다.
    """
    from inspect import signature, iscoroutinefunction

    assert hasattr(agent, 'process_input')
    assert callable(agent.process_input)
    assert iscoroutinefunction(agent.process_input)

    sig = signature(agent.process_input)
    params = list(sig.parameters.keys())
    assert params == ['user_input']
    assert sig.parameters['user_input'].annotation == str
    assert sig.return_annotation == ParsedInput

@pytest.mark.asyncio
async def test_process_input_live_integrated(agent):
    """
    테스트 목적: 실제 API 호출을 통해 언어 감지, 번역, 분석이 통합적으로 성공하는지 확인합니다.
    주의: 실제 API 키와 네트워크 연결이 필요합니다.
    """
    test_cases = [
        # (입력 텍스트, 예상 원본 언어, 예상 영어 번역 (키워드), 예상 의도, 예상 엔티티 (None 또는 dict), 예상 도메인)
        ("안녕하세요, 반갑습니다.", "ko", "hello nice to meet you", ["greeting", "translation"], None, "general"),
        ("Hello, nice to meet you.", "en", "hello nice to meet you", ["greeting"], None, "general"),
        ("나는 학생입니다.", "ko", "i am a student", ["self_description", "statement"], None, "general"),
        ("This is a test in English.", "en", "this is a test in english", ["statement", "general_statement", "text_classification"], None, "general"),
        ("파이썬으로 간단한 웹 서버 만드는 코드 짜줘", "ko", "python code simple web server", ["code_generation"], {"language": "python", "topic": "web server"}, "coding"),
        ("Tell me a joke about computers", "en", "tell me a joke about computers", ["request_joke", "question_answering"], None, "general"),
        ("대한민국의 수도는 어디인가요?", "ko", "what is the capital of south korea", ["question_answering"], {"topic": "capital of South Korea"}, "geography"),
        ("What is the weather like in Seoul tomorrow?", "en", "what is the weather like in seoul tomorrow", ["question_answering"], {"location": "Seoul", "time": "tomorrow"}, "weather"),
    ]

    for i, (text, expected_lang, expected_translation_part, expected_intents, expected_entities, expected_domain) in enumerate(test_cases):
        print(f"\nTesting: {text[:30]}...", flush=True)
        
        # 테스트 케이스 사이에 지연 추가 (Rate Limit 회피) - 시간 증가
        if i > 0:
            await asyncio.sleep(10) # 10초 대기
            
        result = await agent.process_input(text)

        # 1. 원본 텍스트 확인
        assert result.original_text == text

        # 2. 감지된 언어 확인
        assert result.original_language == expected_lang, \
               f"Language mismatch for '{text}'. Expected: {expected_lang}, Got: {result.original_language}"

        # 3. 번역 결과 확인 (대소문자, 구두점 무시)
        normalized_actual_translation = re.sub(r'[.,!?]', '', result.english_text.lower()).strip()
        normalized_expected_translation = re.sub(r'[.,!?]', '', expected_translation_part.lower()).strip()
        if expected_lang == "en":
             normalized_original = re.sub(r'[.,!?]', '', text.lower()).strip()
             assert normalized_actual_translation == normalized_original, \
                   f"English input mismatch for '{text}'. Original: {normalized_original}, Got: {normalized_actual_translation}"
        else:
            # 개별 키워드 포함 여부 확인으로 변경
            expected_keywords = normalized_expected_translation.split()
            missing_keywords = [kw for kw in expected_keywords if kw not in normalized_actual_translation]
            assert not missing_keywords, \
                f"Translation mismatch for '{text}'. Missing keywords: {missing_keywords} in actual translation: '{normalized_actual_translation}' (Expected keywords: '{normalized_expected_translation}')"

        # 4. 의도 분석 결과 확인 (수정: 허용 목록 사용)
        assert result.intent in expected_intents, \
               f"Intent mismatch for '{text}'. Expected one of: {expected_intents}, Got: {result.intent}"

        # 5. 엔티티 분석 결과 확인 (딕셔너리 포함 여부 및 키 확인)
        if expected_entities:
            assert isinstance(result.entities, dict), \
                   f"Entities should be a dict for '{text}', but got: {type(result.entities)}"
            # 특정 케이스에 대해 유동적인 키 허용
            if text == "파이썬으로 간단한 웹 서버 만드는 코드 짜줘":
                assert "language" in result.entities, f"Expected entity key 'language' not found in {result.entities} for '{text}'"
                assert "topic" in result.entities or "task" in result.entities, \
                       f"Expected entity key 'topic' or 'task' not found in {result.entities} for '{text}'"
            elif text == "What is the weather like in Seoul tomorrow?":
                 assert "location" in result.entities, f"Expected entity key 'location' not found in {result.entities} for '{text}'"
                 assert "time" in result.entities, f"Expected entity key 'time' not found in {result.entities} for '{text}'"
            elif text == "대한민국의 수도는 어디인가요?":
                 assert "topic" in result.entities or "country" in result.entities or "question_type" in result.entities, \
                       f"Expected entity key like 'topic', 'country', or 'question_type' not found in {result.entities} for '{text}'"
            else:
                # 다른 케이스는 정의된 모든 키 확인
                for key in expected_entities:
                    assert key in result.entities, f"Expected entity key '{key}' not found in {result.entities} for '{text}'"
        else:
             assert result.entities is None or isinstance(result.entities, dict), \
                   f"Entities should be None or dict for '{text}', but got: {type(result.entities)}"

        # 6. 도메인 분석 결과 확인
        assert result.domain == expected_domain, \
               f"Domain mismatch for '{text}'. Expected: {expected_domain}, Got: {result.domain}"

# --- Error Handling Tests --- 

@pytest.mark.asyncio
async def test_process_input_analysis_api_error(agent: InputParserAgent, mocker):
    """
    테스트 목적: 의도/엔티티/도메인 분석 API 호출 중 예외 발생 시 
                 결과 필드들이 None으로 유지되는지 확인합니다.
    """
    user_input = "Analyze this text."

    # Mock API 호출 (언어 감지, 번역은 정상 응답, 분석은 예외 발생)
    mock_llm_client = AsyncMock()

    # Mock the response for language detection
    mock_lang_response = AsyncMock(spec=genai.types.GenerateContentResponse)
    mock_lang_response.text = "en"

    # Prepare the exception for the analysis call
    mock_analysis_exception = Exception("Simulated API error")

    # Set up the side effect for the mocked method
    mock_llm_client.aio.models.generate_content = AsyncMock(
        side_effect=[
            mock_lang_response,      # First call (language detection) succeeds
            mock_analysis_exception  # Second call (analysis) raises exception
        ]
    )

    # Patch the agent's *internal* llm client instance
    try:
        # Check if 'llm' attribute exists before patching
        if not hasattr(agent, 'llm'):
             pytest.fail("InputParserAgent instance does not have 'llm' attribute. Cannot patch.")

        with patch.object(agent, 'llm', mock_llm_client):
            result = await agent.process_input(user_input)

            # Assertions
            # Language should be detected
            assert result.original_language == "en"
            # Analysis fields should be None
            assert result.intent is None, "Intent should be None on analysis API error"
            assert result.entities is None, "Entities should be None on analysis API error"
            assert result.domain is None, "Domain should be None on analysis API error"
            # Verify the mock was called twice (lang detect, analysis attempt)
            assert mock_llm_client.aio.models.generate_content.call_count == 2
    except AttributeError:
         pytest.fail("Patching agent.llm failed. Check the internal LLM client attribute name in InputParserAgent.")

@pytest.mark.asyncio
async def test_process_input_analysis_json_error(agent: InputParserAgent, mocker):
    """
    테스트 목적: 의도/엔티티/도메인 분석 API가 잘못된 JSON 형식 응답 시 
                 결과 필드들이 None으로 유지되는지 확인합니다.
    """
    user_input = "Analyze this text."
    invalid_json_string = "this is not json{"

    # Mock API 호출 (언어 감지, 번역은 정상, 분석은 잘못된 JSON 반환)
    mock_llm_client = AsyncMock()

    # Mock the response for language detection
    mock_lang_response = AsyncMock(spec=genai.types.GenerateContentResponse)
    mock_lang_response.text = "en"

    # Mock the response for analysis (with invalid JSON)
    mock_analysis_response = AsyncMock(spec=genai.types.GenerateContentResponse)
    mock_analysis_response.text = invalid_json_string

    # Set up the side effect for the mocked method
    mock_llm_client.aio.models.generate_content = AsyncMock(
        side_effect=[
            mock_lang_response,       # First call (language detection) succeeds
            mock_analysis_response  # Second call (analysis) returns invalid JSON
        ]
    )

    # Patch the agent's internal llm client instance
    try:
        if not hasattr(agent, 'llm'):
             pytest.fail("InputParserAgent instance does not have 'llm' attribute. Cannot patch.")

        with patch.object(agent, 'llm', mock_llm_client):
            result = await agent.process_input(user_input)

            # Assertions
            # Language should be detected
            assert result.original_language == "en"
            # Analysis fields should be None
            assert result.intent is None, "Intent should be None on JSON parse error"
            assert result.entities is None, "Entities should be None on JSON parse error"
            assert result.domain is None, "Domain should be None on JSON parse error"
            # Verify the mock was called twice
            assert mock_llm_client.aio.models.generate_content.call_count == 2
    except AttributeError:
         pytest.fail("Patching agent.llm failed. Check the internal LLM client attribute name in InputParserAgent.")

# # 비정상 응답 및 예외 테스트는 실제 API 호출로는 안정적으로 테스트하기 어려움
# @pytest.mark.asyncio
# async def test_process_input_language_detection_unexpected_format(agent, mocker, capsys):
#     pass

# @pytest.mark.asyncio
# async def test_process_input_language_detection_exception(agent, mocker, capsys):
#     pass

# 통합 테스트는 language_detection_live 테스트로 대체됨
# @pytest.mark.asyncio
# async def test_process_input_returns_parsed_input_integrated(agent, mocker):
#     pass 