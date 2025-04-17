"""
InputParserAgent 클래스 테스트
"""

import pytest
import sys
import os
import asyncio
from pathlib import Path
from google.adk.agents import LlmAgent

# 테스트 대상 모듈을 sys.path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# 환경 변수 로드 시도 (테스트 환경에 .env 파일이 있을 경우)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # python-dotenv가 설치되지 않아도 테스트는 진행 가능

from jarvis.components.input_parser import InputParserAgent
from jarvis.models.input import ParsedInput

@pytest.fixture
def agent():
    """InputParserAgent 인스턴스를 생성하는 fixture"""
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
    # 모델 ID가 설정되었는지 확인
    assert hasattr(agent, 'model') # model 속성 존재 확인
    assert agent.model == "gemini-1.5-flash"

def test_process_input_method_signature(agent):
    """
    테스트 목적: process_input 메서드의 시그니처(인자, 반환 타입)를 확인합니다.
    """
    from inspect import signature, iscoroutinefunction
    
    assert hasattr(agent, 'process_input')
    assert callable(agent.process_input)
    assert iscoroutinefunction(agent.process_input) # 비동기 함수인지 확인
    
    sig = signature(agent.process_input)
    # 파라미터 확인 ('self' 제외)
    params = list(sig.parameters.keys()) 
    assert params == ['user_input']
    # 파라미터 타입 힌트 확인
    assert sig.parameters['user_input'].annotation == str
    # 반환 타입 힌트 확인
    assert sig.return_annotation == ParsedInput

@pytest.mark.asyncio # 비동기 테스트 실행
async def test_process_input_returns_parsed_input(agent):
    """
    테스트 목적: process_input 메서드가 ParsedInput 객체를 반환하는지 확인합니다. (현재 임시 구현)
    """
    test_input = "테스트 입력"
    result = await agent.process_input(test_input)
    assert isinstance(result, ParsedInput)
    # 현재는 임시 구현이므로 상세 내용 검증은 생략하고 타입만 확인
    assert result.original_text == test_input # 임시 구현 검증
    assert result.original_language == "ko" # 임시 구현 검증
    assert result.english_text == test_input # 임시 구현 검증 