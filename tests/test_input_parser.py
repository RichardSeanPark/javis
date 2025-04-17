"""
입력 처리 및 파싱 계층 테스트
"""

import os
import sys
import inspect
import asyncio
import pytest
import json
from typing import Dict, Any, Optional

# 현재 작업 디렉토리를 sys.path에 추가하여 src 모듈을 불러올 수 있게 합니다
sys.path.insert(0, os.getcwd())

# 테스트할 모듈을 임포트합니다
from src.jarvis.models.input import ParsedInput
from src.jarvis.components.input_parser import InputParserAgent


class TestParsedInputModel:
    """
    ParsedInput 데이터 모델 테스트 클래스
    """
    
    def test_file_exists(self):
        """
        테스트 목적: src/jarvis/models/input.py 파일이 존재하는지 확인합니다.
        테스트 방법: 파일이 존재하고 적절한 클래스가 정의되어 있는지 확인합니다.
        """
        from pathlib import Path
        
        # 파일 존재 확인
        file_path = Path("src/jarvis/models/input.py")
        assert file_path.exists(), "src/jarvis/models/input.py 파일이 존재하지 않습니다."
    
    def test_inherits_from_base_model(self):
        """
        테스트 목적: ParsedInput 클래스가 pydantic의 BaseModel을 상속하는지 확인합니다.
        테스트 방법: 클래스의 MRO(Method Resolution Order)를 확인합니다.
        """
        from pydantic import BaseModel
        
        # BaseModel 상속 확인
        assert issubclass(ParsedInput, BaseModel), "ParsedInput이 pydantic의 BaseModel을 상속하지 않습니다."
    
    def test_required_fields_exist(self):
        """
        테스트 목적: 필수 필드(original_text, original_language, english_text)가 존재하는지 확인합니다.
        테스트 방법: 필드의 존재 여부와 타입을 확인합니다.
        """
        # 필드 존재 확인
        field_annotations = ParsedInput.__annotations__
        
        assert "original_text" in field_annotations, "original_text 필드가 존재하지 않습니다."
        assert field_annotations["original_text"] == str, "original_text 필드의 타입이 str이 아닙니다."
        
        assert "original_language" in field_annotations, "original_language 필드가 존재하지 않습니다."
        assert field_annotations["original_language"] == str, "original_language 필드의 타입이 str이 아닙니다."
        
        assert "english_text" in field_annotations, "english_text 필드가 존재하지 않습니다."
        assert field_annotations["english_text"] == str, "english_text 필드의 타입이 str이 아닙니다."
    
    def test_optional_fields_exist(self):
        """
        테스트 목적: 선택적 필드(intent, entities, domain)가 존재하는지 확인합니다.
        테스트 방법: 필드의 존재 여부를 확인합니다.
        """
        # 필드 존재 확인
        field_annotations = ParsedInput.__annotations__
        
        assert "intent" in field_annotations, "intent 필드가 존재하지 않습니다."
        assert "entities" in field_annotations, "entities 필드가 존재하지 않습니다."
        assert "domain" in field_annotations, "domain 필드가 존재하지 않습니다."
    
    def test_field_types_and_defaults(self):
        """
        테스트 목적: 각 필드의 타입 및 기본값 설정을 확인합니다.
        테스트 방법: 선택적 필드의 기본값이 None으로 설정되어 있는지 확인합니다.
        """
        # 필드 기본값 확인
        obj = ParsedInput(
            original_text="Test",
            original_language="en",
            english_text="Test"
        )
        
        assert obj.intent is None, "intent 필드의 기본값이 None이 아닙니다."
        assert obj.entities is None, "entities 필드의 기본값이 None이 아닙니다."
        assert obj.domain is None, "domain 필드의 기본값이 None이 아닙니다."
    
    def test_json_serialization(self):
        """
        테스트 목적: JSON 직렬화/역직렬화가 올바르게 작동하는지 확인합니다.
        테스트 방법: 객체를 JSON으로 변환한 후 다시 객체로 변환하여 비교합니다.
        """
        # 테스트 객체 생성
        original = ParsedInput(
            original_text="안녕하세요",
            original_language="ko",
            english_text="Hello",
            intent="greeting",
            entities={"greeting": "formal"},
            domain="conversation"
        )
        
        # JSON 직렬화
        json_str = original.model_dump_json()
        
        # JSON 역직렬화
        restored = ParsedInput.model_validate_json(json_str)
        
        # 비교
        assert restored.original_text == original.original_text
        assert restored.original_language == original.original_language
        assert restored.english_text == original.english_text
        assert restored.intent == original.intent
        assert restored.entities == original.entities
        assert restored.domain == original.domain


class TestInputParserAgent:
    """
    InputParserAgent 클래스 테스트
    """
    
    def test_file_exists(self):
        """
        테스트 목적: src/jarvis/components/input_parser.py 파일이 존재하는지 확인합니다.
        테스트 방법: 파일 존재 여부를 확인합니다.
        """
        from pathlib import Path
        
        # 파일 존재 확인
        file_path = Path("src/jarvis/components/input_parser.py")
        assert file_path.exists(), "src/jarvis/components/input_parser.py 파일이 존재하지 않습니다."
    
    def test_inherits_from_agent(self):
        """
        테스트 목적: InputParserAgent 클래스가 Agent를 상속하는지 확인합니다.
        테스트 방법: 클래스의 MRO(Method Resolution Order)를 확인합니다.
        """
        from google.adk import Agent
        
        # Agent 상속 확인
        assert issubclass(InputParserAgent, Agent), "InputParserAgent가 Agent를 상속하지 않습니다."
    
    def test_init_configuration(self):
        """
        테스트 목적: __init__ 메서드에서 적절한 이름과 설명이 이루어지는지 확인합니다.
        테스트 방법: 인스턴스 생성 후 속성 값을 확인합니다.
        """
        # 인스턴스 생성
        parser = InputParserAgent()
        
        # 설정 확인
        assert parser.name == "InputParser", "에이전트 이름이 InputParser가 아닙니다."
        assert "parses user input" in parser.description.lower(), "설명이 적절하지 않습니다."
        assert hasattr(parser, "model"), "model 속성이 없습니다."
    
    def test_process_input_method_exists(self):
        """
        테스트 목적: process_input 메서드가 존재하는지 확인합니다.
        테스트 방법: 메서드의 존재 여부와 비동기 함수인지 확인합니다.
        """
        # 메서드 존재 확인
        assert hasattr(InputParserAgent, "process_input"), "process_input 메서드가 존재하지 않습니다."
        
        # 비동기 함수 확인
        assert asyncio.iscoroutinefunction(InputParserAgent.process_input), "process_input이 비동기 함수가 아닙니다."
    
    def test_detect_language_method_exists(self):
        """
        테스트 목적: _detect_language 메서드가 존재하는지 확인합니다.
        테스트 방법: 메서드의 존재 여부와 비동기 함수인지 확인합니다.
        """
        # 메서드 존재 확인
        assert hasattr(InputParserAgent, "_detect_language"), "_detect_language 메서드가 존재하지 않습니다."
        
        # 비동기 함수 확인
        assert asyncio.iscoroutinefunction(InputParserAgent._detect_language), "_detect_language가 비동기 함수가 아닙니다."
    
    def test_translate_to_english_method_exists(self):
        """
        테스트 목적: _translate_to_english 메서드가 존재하는지 확인합니다.
        테스트 방법: 메서드의 존재 여부와 비동기 함수인지 확인합니다.
        """
        # 메서드 존재 확인
        assert hasattr(InputParserAgent, "_translate_to_english"), "_translate_to_english 메서드가 존재하지 않습니다."
        
        # 비동기 함수 확인
        assert asyncio.iscoroutinefunction(InputParserAgent._translate_to_english), "_translate_to_english가 비동기 함수가 아닙니다."
    
    def test_analyze_intent_and_entities_method_exists(self):
        """
        테스트 목적: _analyze_intent_and_entities 메서드가 존재하는지 확인합니다.
        테스트 방법: 메서드의 존재 여부와 비동기 함수인지 확인합니다.
        """
        # 메서드 존재 확인
        assert hasattr(InputParserAgent, "_analyze_intent_and_entities"), "_analyze_intent_and_entities 메서드가 존재하지 않습니다."
        
        # 비동기 함수 확인
        assert asyncio.iscoroutinefunction(InputParserAgent._analyze_intent_and_entities), \
            "_analyze_intent_and_entities가 비동기 함수가 아닙니다."
    
    def test_module_registration(self):
        """
        테스트 목적: src/jarvis/components/__init__.py에 InputParserAgent 모듈이 등록되어 있는지 확인합니다.
        테스트 방법: 모듈 임포트가 가능한지 확인합니다.
        """
        try:
            from src.jarvis.components import InputParserAgent as RegisteredAgent
            assert RegisteredAgent == InputParserAgent, "등록된 InputParserAgent가 원본과 일치하지 않습니다."
        except ImportError:
            pytest.fail("src/jarvis/components에서 InputParserAgent를 임포트할 수 없습니다.")


@pytest.mark.asyncio
class TestInputParserIntegration:
    """
    InputParserAgent 통합 테스트
    
    참고: 이 테스트는 실제 Gemini API를 호출하므로 환경 변수 설정이 필요합니다.
    실제 환경에서 실행하려면 GEMINI_API_KEY 환경 변수가 설정되어 있어야 합니다.
    """
    
    # 이 테스트 클래스의 모든 테스트는 막아 두고, 필요시 개별적으로 활성화하세요.
    # 실제 API 호출이 필요하므로 자동화된 CI/CD 파이프라인에서는 실행하지 않는 것이 좋습니다.
    
    @pytest.mark.skip(reason="실제 API 호출이 필요합니다. 개별 테스트시 활성화하세요.")
    async def test_detect_language_en(self):
        """
        테스트 목적: 영어 텍스트 입력 시 'en' 반환을 확인합니다.
        테스트 방법: 영어 텍스트에 대해 _detect_language 호출 후 결과를 확인합니다.
        """
        parser = InputParserAgent()
        result = await parser._detect_language("Hello, how are you today?")
        assert result == "en", f"영어 텍스트에 대해 'en'이 아닌 '{result}'가 반환되었습니다."
    
    @pytest.mark.skip(reason="실제 API 호출이 필요합니다. 개별 테스트시 활성화하세요.")
    async def test_detect_language_ko(self):
        """
        테스트 목적: 한국어 텍스트 입력 시 'ko' 반환을 확인합니다.
        테스트 방법: 한국어 텍스트에 대해 _detect_language 호출 후 결과를 확인합니다.
        """
        parser = InputParserAgent()
        result = await parser._detect_language("안녕하세요, 오늘 기분이 어떠신가요?")
        assert result == "ko", f"한국어 텍스트에 대해 'ko'가 아닌 '{result}'가 반환되었습니다."
    
    @pytest.mark.skip(reason="실제 API 호출이 필요합니다. 개별 테스트시 활성화하세요.")
    async def test_translate_korean_to_english(self):
        """
        테스트 목적: 한국어 텍스트 입력 시 올바른 영어 번역 반환을 확인합니다.
        테스트 방법: 한국어 텍스트에 대해 _translate_to_english 호출 후 결과를 확인합니다.
        """
        parser = InputParserAgent()
        korean_text = "안녕하세요, 오늘 날씨가 좋네요."
        result = await parser._translate_to_english(korean_text, "ko")
        
        # 번역은 다양한 형태가 가능하므로 단어 포함 여부로 확인
        assert "hello" in result.lower() or "hi" in result.lower(), "인사말이 번역되지 않았습니다."
        assert "weather" in result.lower(), "날씨에 대한 언급이 번역되지 않았습니다."
        assert "good" in result.lower() or "nice" in result.lower(), "좋다는 표현이 번역되지 않았습니다."
    
    @pytest.mark.skip(reason="실제 API 호출이 필요합니다. 개별 테스트시 활성화하세요.")
    async def test_analyze_coding_intent(self):
        """
        테스트 목적: 코딩 관련 텍스트 입력 시 의도와 도메인 분석을 확인합니다.
        테스트 방법: 코딩 요청 텍스트에 대해 _analyze_intent_and_entities 호출 후 결과를 확인합니다.
        """
        parser = InputParserAgent()
        text = "Write a Python function to calculate Fibonacci numbers"
        intent, entities, domain = await parser._analyze_intent_and_entities(text)
        
        assert intent and "code" in intent.lower(), f"코딩 의도가 감지되지 않았습니다: {intent}"
        assert domain and "coding" in domain.lower(), f"코딩 도메인이 감지되지 않았습니다: {domain}"
        assert entities and "python" in str(entities).lower(), f"Python 엔티티가 감지되지 않았습니다: {entities}"
    
    @pytest.mark.skip(reason="실제 API 호출이 필요합니다. 개별 테스트시 활성화하세요.")
    async def test_full_input_processing_english(self):
        """
        테스트 목적: 영어 입력에 대한 전체 처리 과정을 확인합니다.
        테스트 방법: 영어 텍스트에 대해 process_input 호출 후 결과 객체를 확인합니다.
        """
        parser = InputParserAgent()
        text = "What is the capital of France?"
        result = await parser.process_input(text)
        
        assert isinstance(result, ParsedInput), "결과가 ParsedInput 객체가 아닙니다."
        assert result.original_text == text, "원본 텍스트가 보존되지 않았습니다."
        assert result.original_language == "en", f"원본 언어가 'en'이 아닌 '{result.original_language}'로 감지되었습니다."
        assert result.english_text == text, "영어 텍스트가 원본과 동일하지 않습니다."
        assert result.intent and "question" in result.intent.lower(), f"질문 의도가 감지되지 않았습니다: {result.intent}"
        assert result.domain, "도메인이 설정되지 않았습니다."
        assert result.entities and "france" in str(result.entities).lower(), "France 엔티티가 감지되지 않았습니다."
    
    @pytest.mark.skip(reason="실제 API 호출이 필요합니다. 개별 테스트시 활성화하세요.")
    async def test_full_input_processing_korean(self):
        """
        테스트 목적: 한국어 입력에 대한 전체 처리 과정을 확인합니다.
        테스트 방법: 한국어 텍스트에 대해 process_input 호출 후 결과 객체를 확인합니다.
        """
        parser = InputParserAgent()
        text = "파이썬으로 간단한 웹 크롤러를 만들어줘"
        result = await parser.process_input(text)
        
        assert isinstance(result, ParsedInput), "결과가 ParsedInput 객체가 아닙니다."
        assert result.original_text == text, "원본 텍스트가 보존되지 않았습니다."
        assert result.original_language == "ko", f"원본 언어가 'ko'가 아닌 '{result.original_language}'로 감지되었습니다."
        assert result.english_text and "python" in result.english_text.lower(), "영어 번역에 'python'이 포함되지 않습니다."
        assert result.intent and "code" in result.intent.lower(), f"코드 생성 의도가 감지되지 않았습니다: {result.intent}"
        assert result.domain and "coding" in result.domain.lower(), f"코딩 도메인이 감지되지 않았습니다: {result.domain}"
        assert result.entities, "엔티티가 추출되지 않았습니다." 