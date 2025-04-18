# tests/agents/test_coding_agent.py

import pytest
import sys
import os
from pathlib import Path

# Add src directory to sys.path to allow importing modules from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import necessary classes
from google.adk.agents import LlmAgent
from jarvis.agents.coding_agent import CodingAgent, DEFAULT_CODING_MODEL

# Define the expected default values based on coding_agent.py
EXPECTED_DEFAULT_NAME = "CodingAgent"
EXPECTED_DEFAULT_DESCRIPTION = "Generates, analyzes, debugs, and optimizes code based on user requests in English."
EXPECTED_DEFAULT_INSTRUCTION = (
    "You are an expert coding assistant. Analyze the provided English request "
    "and any accompanying code snippets. Generate improved code, explain code, "
    "debug errors, or optimize code as requested. Use the available tools "
    "for code execution or linting if necessary and permitted. "
    "Respond only in English with the code result or explanation."
)

@pytest.fixture
def coding_agent():
    """Fixture to create a default CodingAgent instance."""
    return CodingAgent()

def test_coding_agent_file_exists():
    """
    테스트 목적: src/jarvis/agents/coding_agent.py 파일이 존재하는지 확인합니다.
    """
    agent_path = Path('src/jarvis/agents/coding_agent.py')
    assert agent_path.exists(), f"{agent_path} 파일이 존재하지 않습니다."
    assert agent_path.is_file(), f"{agent_path} 는 파일이어야 합니다."

def test_coding_agent_inherits_llm_agent():
    """
    테스트 목적: CodingAgent 클래스가 LlmAgent를 상속하는지 확인합니다.
    """
    assert issubclass(CodingAgent, LlmAgent), "CodingAgent는 LlmAgent를 상속해야 합니다."

def test_coding_agent_default_initialization(coding_agent):
    """
    테스트 목적: CodingAgent 인스턴스가 기본값으로 정상적으로 생성되는지 확인합니다.
    """
    assert coding_agent is not None, "CodingAgent 인스턴스 생성에 실패했습니다."
    assert isinstance(coding_agent, CodingAgent), "생성된 객체가 CodingAgent 타입이 아닙니다."

def test_coding_agent_default_attributes(coding_agent):
    """
    테스트 목적: 기본값으로 생성된 CodingAgent 인스턴스의 속성들을 확인합니다.
    """
    assert coding_agent.name == EXPECTED_DEFAULT_NAME, \
        f"기본 이름이 '{EXPECTED_DEFAULT_NAME}' 이어야 합니다. 실제: '{coding_agent.name}'"
    assert coding_agent.description == EXPECTED_DEFAULT_DESCRIPTION, \
        f"기본 설명이 '{EXPECTED_DEFAULT_DESCRIPTION}' 이어야 합니다. 실제: '{coding_agent.description}'"
    assert coding_agent.model == DEFAULT_CODING_MODEL, \
        f"기본 모델이 '{DEFAULT_CODING_MODEL}' 이어야 합니다. 실제: '{coding_agent.model}'"
    assert coding_agent.instruction == EXPECTED_DEFAULT_INSTRUCTION, \
        f"기본 지침이 '{EXPECTED_DEFAULT_INSTRUCTION}' 이어야 합니다. 실제: '{coding_agent.instruction}'"
    # Tool은 아직 구현되지 않았으므로 비어 있거나 None 이어야 함 (LlmAgent 기본값 확인)
    assert not coding_agent.tools, f"기본 tools 속성은 비어 있어야 합니다. 실제: {coding_agent.tools}"

def test_coding_agent_initialization_with_args():
    """
    테스트 목적: __init__에 인자를 전달하여 CodingAgent 인스턴스 생성 시 속성이 올바르게 설정되는지 확인합니다.
    """
    custom_name = "MyCodingBot"
    custom_desc = "A custom coding helper."
    custom_model = "gemini-pro-code"
    # instruction은 __init__에서 직접 받지 않으므로 기본값이 유지되어야 함

    agent = CodingAgent(
        name=custom_name,
        description=custom_desc,
        model=custom_model
    )

    assert agent.name == custom_name
    assert agent.description == custom_desc
    assert agent.model == custom_model
    # Instruction should remain the default defined in the class
    assert agent.instruction == EXPECTED_DEFAULT_INSTRUCTION
    assert not agent.tools # Tools are not passed or handled yet

# TODO: Add tests for tool registration once implemented (Step 5)
# TODO: Add tests for agent behavior (LLM calls, tool usage) once tools are implemented 