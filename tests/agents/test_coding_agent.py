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
from src.jarvis.tools import code_execution_tool # Import the actual tool

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
    # Check that the code execution tool is present by name
    assert any(hasattr(tool, 'name') and tool.name == 'execute_python_code' for tool in coding_agent.tools), \
        f"기본 tools 속성에 'execute_python_code' 툴이 포함되어야 합니다. 실제: {[getattr(t, 'name', None) for t in coding_agent.tools]}"

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
        # tools는 명시적으로 전달하지 않아도 __init__에서 추가됨
    )

    assert agent.name == custom_name
    assert agent.description == custom_desc
    assert agent.model == custom_model
    # Instruction should remain the default defined in the class
    assert agent.instruction == EXPECTED_DEFAULT_INSTRUCTION
    # Check that the code execution tool is present by name
    assert any(hasattr(tool, 'name') and tool.name == 'execute_python_code' for tool in agent.tools), \
        f"인자 전달 시에도 tools 속성에 'execute_python_code' 툴이 포함되어야 합니다. 실제: {[getattr(t, 'name', None) for t in agent.tools]}"

def test_coding_agent_instantiation():
    """4.1: CodingAgent 인스턴스 생성 테스트 (기본값 사용)"""
    try:
        agent = CodingAgent()
        assert agent is not None
        assert agent.name == "CodingAgent"
        assert agent.description == "Generates, analyzes, debugs, and optimizes code based on user requests in English."
        # Add more assertions for default model, instruction etc. if needed
    except Exception as e:
        pytest.fail(f"CodingAgent instantiation with defaults failed: {e}")

def test_coding_agent_initialization_registers_tool():
    """4.1 / 툴 등록 테스트: CodingAgent.__init__에서 code_execution_tool이 tools 리스트에 명시적으로 추가되는지 확인"""
    agent = CodingAgent()
    # Check for the tool's presence by name instead of object identity
    assert any(hasattr(tool, 'name') and tool.name == 'execute_python_code' for tool in agent.tools), \
        f"tools 속성에 'execute_python_code' 툴이 포함되어야 합니다. 실제: {[getattr(t, 'name', None) for t in agent.tools]}"

def test_coding_agent_instantiation_with_args():
    """4.1: CodingAgent 인스턴스 생성 테스트 (인자 전달)"""
    custom_name = "MyCoder"
    custom_desc = "My description"
    custom_model = "gemini-pro"
    custom_instruction = "Be brief."
    # Pass an empty tools list initially to ensure the agent adds its own
    agent = CodingAgent(
        name=custom_name,
        description=custom_desc,
        model=custom_model,
        instruction=custom_instruction,
        tools=[] # Pass empty list
    )
    assert agent.name == custom_name
    assert agent.description == custom_desc
    assert agent.model == custom_model
    assert agent.instruction == custom_instruction
    # Ensure the code execution tool was added even if an empty list was passed
    # Check by name
    assert any(hasattr(tool, 'name') and tool.name == 'execute_python_code' for tool in agent.tools), \
        f"빈 tools 리스트 전달 시에도 'execute_python_code' 툴이 포함되어야 합니다. 실제: {[getattr(t, 'name', None) for t in agent.tools]}"
    # Optionally, check the number of tools if no others should be present
    assert len(agent.tools) == 1

# TODO: Add tests for tool registration once implemented (Step 5)
# TODO: Add tests for agent behavior (LLM calls, tool usage) once tools are implemented 