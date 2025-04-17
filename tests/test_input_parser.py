"""
InputParserAgent 클래스 테스트 (실제 API 호출 사용)
"""

import pytest
import sys
import os
import asyncio
import re # re 임포트 추가
from pathlib import Path
from google.adk.agents import LlmAgent # 수정: LlmAgent 임포트 확인 (test_input_parser_inherits_llm_agent 위해)

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

def test_input_parser_inherits_llm_agent(agent):
    """
    테스트 목적: InputParserAgent 클래스가 LlmAgent를 상속하는지 확인합니다.
    """
    assert isinstance(agent, LlmAgent)

def test_input_parser_initialization(agent):
    """
    테스트 목적: __init__ 메서드가 올바른 이름, 설명, 모델 ID로 초기화되는지 확인합니다.
    """
    assert agent.name == "InputParser"
    assert agent.description == "Parses user input: detects language, translates to English, and analyzes intent, entities, and domain."
    assert hasattr(agent, 'model')
    assert agent.model == "gemini-1.5-flash"

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
async def test_process_input_language_detection_and_translation_live(agent):
    """
    테스트 목적: 실제 API 호출을 통해 언어 감지 및 영어 번역이 성공하는지 확인합니다.
    주의: 실제 API 키와 네트워크 연결이 필요합니다.
    """
    test_cases = [
        # (입력 텍스트, 예상 원본 언어, 예상 영어 번역 (일부 또는 키워드))
        ("안녕하세요, 반갑습니다.", "ko", "hello nice to meet you"), # 대소문자 무시, 구두점 무시 비교
        ("Hello, nice to meet you.", "en", "hello nice to meet you"), # 영어는 그대로
        ("こんにちは、はじめまして。", "ja", "hello nice to meet you"),
        ("Bonjour, enchanté.", "fr", "hello pleased to meet you"),
        ("你好，很高兴认识你。", "zh", "hello nice to meet you"),
        # 다른 예시 추가 가능
        ("나는 학생입니다.", "ko", "i am a student"),
        ("저는 오늘 공원에 갔습니다.", "ko", "i went to the park today"),
        ("This is a test in English.", "en", "this is a test in english"),
    ]

    for text, expected_lang, expected_translation_part in test_cases:
        print(f"\nTesting: {text[:30]}... (Expected lang: {expected_lang})", flush=True)
        result = await agent.process_input(text)

        # 1. 원본 텍스트 확인
        assert result.original_text == text

        # 2. 감지된 언어 확인
        assert result.original_language == expected_lang, \
               f"Language mismatch for '{text}'. Expected: {expected_lang}, Got: {result.original_language}"

        # 3. 번역 결과 확인 (대소문자, 구두점 무시, 일부 포함 여부)
        # 실제 번역 결과는 모델에 따라 약간씩 다를 수 있으므로 핵심 내용 포함 여부 확인
        # 구두점 제거 로직 수정: strip -> re.sub
        normalized_actual = re.sub(r'[.,!?]', '', result.english_text.lower()).strip()
        normalized_expected = re.sub(r'[.,!?]', '', expected_translation_part.lower()).strip()

        # 영어 입력의 경우, 원본과 번역 결과가 동일해야 함 (정규화 후 비교)
        if expected_lang == "en":
             # 영어 원본도 동일하게 정규화
             normalized_original = re.sub(r'[.,!?]', '', text.lower()).strip()
             assert normalized_actual == normalized_original, \
                   f"English input mismatch for '{text}'. Original: {normalized_original}, Got: {normalized_actual}"
        else:
            # 다른 언어의 경우, 예상 번역 키워드가 포함되어 있는지 확인
            # 더 정확한 비교를 위해 유사도 라이브러리 사용 고려 가능
            # 비교 로직은 그대로 유지 (포함 여부 확인)
            assert normalized_expected in normalized_actual or normalized_actual in normalized_expected , \
                   f"Translation mismatch for '{text}'. Expected part: '{normalized_expected}', Got: '{normalized_actual}'"

        # TODO: intent, entities, domain은 아직 None인지 확인
        assert result.intent is None
        assert result.entities is None
        assert result.domain is None

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