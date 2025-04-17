"""
ParsedInput 데이터 모델 테스트
"""

import pytest
from pydantic import ValidationError, BaseModel
from pathlib import Path
import sys
import os

# 테스트 대상 모듈을 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from jarvis.models.input import ParsedInput

def test_input_model_file_exists():
    """
    테스트 목적: src/jarvis/models/input.py 파일이 존재하는지 확인합니다.
    """
    model_path = Path('src/jarvis/models/input.py')
    assert model_path.exists(), "src/jarvis/models/input.py 파일이 존재하지 않습니다."

def test_parsed_input_inherits_base_model():
    """
    테스트 목적: ParsedInput 클래스가 BaseModel을 상속하는지 확인합니다.
    """
    assert issubclass(ParsedInput, BaseModel)

def test_parsed_input_required_fields():
    """
    테스트 목적: 필수 필드가 정의되어 있고 누락 시 오류 발생하는지 확인합니다.
    """
    # 필수 필드 정의 확인 (클래스 어노테이션 검사)
    assert 'original_text' in ParsedInput.__annotations__
    assert 'original_language' in ParsedInput.__annotations__
    assert 'english_text' in ParsedInput.__annotations__

    # 필수 필드 누락 시 ValidationError 발생 확인
    with pytest.raises(ValidationError):
        ParsedInput(original_language='ko', english_text='Hello') # original_text 누락
    with pytest.raises(ValidationError):
        ParsedInput(original_text='안녕', english_text='Hello') # original_language 누락
    with pytest.raises(ValidationError):
        ParsedInput(original_text='안녕', original_language='ko') # english_text 누락

def test_parsed_input_optional_fields():
    """
    테스트 목적: 선택적 필드가 정의되어 있는지 확인합니다.
    """
    # 선택적 필드 정의 확인 (클래스 어노테이션 검사)
    assert 'intent' in ParsedInput.__annotations__
    assert 'entities' in ParsedInput.__annotations__
    assert 'domain' in ParsedInput.__annotations__

def test_parsed_input_valid_data():
    """
    테스트 목적: 모든 필드에 올바른 타입의 값을 할당할 수 있는지 확인합니다.
    """
    data = {
        "original_text": "오늘 날씨 어때?",
        "original_language": "ko",
        "english_text": "What's the weather like today?",
        "intent": "weather_query",
        "entities": {"location": "current", "time": "today"},
        "domain": "weather"
    }
    try:
        parsed_input = ParsedInput(**data)
        assert parsed_input.original_text == data["original_text"]
        assert parsed_input.original_language == data["original_language"]
        assert parsed_input.english_text == data["english_text"]
        assert parsed_input.intent == data["intent"]
        assert parsed_input.entities == data["entities"]
        assert parsed_input.domain == data["domain"]
    except ValidationError as e:
        pytest.fail(f"올바른 데이터로 ParsedInput 생성 시 오류 발생: {e}")

def test_parsed_input_optional_fields_as_none():
    """
    테스트 목적: 선택적 필드에 None 값을 할당할 수 있는지 확인합니다.
    """
    data = {
        "original_text": "안녕",
        "original_language": "ko",
        "english_text": "Hello",
        # intent, entities, domain은 None으로 기본 설정됨
    }
    try:
        parsed_input = ParsedInput(**data)
        assert parsed_input.intent is None
        assert parsed_input.entities is None
        assert parsed_input.domain is None
    except ValidationError as e:
        pytest.fail(f"선택적 필드가 None일 때 ParsedInput 생성 시 오류 발생: {e}") 