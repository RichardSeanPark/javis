# tests/agents/test_qa_agent.py

import pytest
import sys
import os
from pathlib import Path

# Add src directory to sys.path to allow importing modules from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import necessary classes
from google.adk.agents import LlmAgent
from jarvis.agents.qa_agent import KnowledgeQA_Agent, DEFAULT_QA_MODEL, DEFAULT_QA_INSTRUCTION

# Define the expected default values based on qa_agent.py
EXPECTED_DEFAULT_NAME = "KnowledgeQA_Agent"
EXPECTED_DEFAULT_DESCRIPTION = "Answers general knowledge questions in English. Can use web search for up-to-date information."

@pytest.fixture
def qa_agent():
    """Fixture to create a default KnowledgeQA_Agent instance."""
    return KnowledgeQA_Agent()

def test_qa_agent_file_exists():
    """
    테스트 목적: src/jarvis/agents/qa_agent.py 파일이 존재하는지 확인합니다.
    """
    agent_path = Path('src/jarvis/agents/qa_agent.py')
    assert agent_path.exists(), f"{agent_path} 파일이 존재하지 않습니다."
    assert agent_path.is_file(), f"{agent_path} 는 파일이어야 합니다."

def test_qa_agent_inherits_llm_agent():
    """
    테스트 목적: KnowledgeQA_Agent 클래스가 LlmAgent를 상속하는지 확인합니다.
    """
    assert issubclass(KnowledgeQA_Agent, LlmAgent), "KnowledgeQA_Agent는 LlmAgent를 상속해야 합니다."

def test_qa_agent_default_initialization(qa_agent):
    """
    테스트 목적: KnowledgeQA_Agent 인스턴스가 기본값으로 정상적으로 생성되는지 확인합니다.
    """
    assert qa_agent is not None, "KnowledgeQA_Agent 인스턴스 생성에 실패했습니다."
    assert isinstance(qa_agent, KnowledgeQA_Agent), "생성된 객체가 KnowledgeQA_Agent 타입이 아닙니다."

def test_qa_agent_default_attributes(qa_agent):
    """
    테스트 목적: 기본값으로 생성된 KnowledgeQA_Agent 인스턴스의 속성들을 확인합니다.
    """
    assert qa_agent.name == EXPECTED_DEFAULT_NAME, \
        f"기본 이름이 '{EXPECTED_DEFAULT_NAME}' 이어야 합니다. 실제: '{qa_agent.name}'"
    assert qa_agent.description == EXPECTED_DEFAULT_DESCRIPTION, \
        f"기본 설명이 '{EXPECTED_DEFAULT_DESCRIPTION}' 이어야 합니다. 실제: '{qa_agent.description}'"
    assert qa_agent.model == DEFAULT_QA_MODEL, \
        f"기본 모델이 '{DEFAULT_QA_MODEL}' 이어야 합니다. 실제: '{qa_agent.model}'"
    assert qa_agent.instruction == DEFAULT_QA_INSTRUCTION, \
        f"기본 지침이 '{DEFAULT_QA_INSTRUCTION}' 이어야 합니다. 실제: '{qa_agent.instruction}'"
    # Tool은 아직 구현되지 않았으므로 비어 있거나 None 이어야 함
    assert not qa_agent.tools, f"기본 tools 속성은 비어 있어야 합니다. 실제: {qa_agent.tools}"

def test_qa_agent_initialization_with_args():
    """
    테스트 목적: __init__에 인자를 전달하여 KnowledgeQA_Agent 인스턴스 생성 시 속성이 올바르게 설정되는지 확인합니다.
    """
    custom_name = "MyQABot"
    custom_desc = "A custom QA helper."
    custom_model = "gemini-pro"
    custom_instruction = "Answer questions briefly."

    agent = KnowledgeQA_Agent(
        name=custom_name,
        description=custom_desc,
        model=custom_model,
        instruction=custom_instruction # Pass custom instruction
    )

    assert agent.name == custom_name
    assert agent.description == custom_desc
    assert agent.model == custom_model
    # Instruction should be the custom one passed
    assert agent.instruction == custom_instruction
    assert not agent.tools # Tools are not passed or handled yet

# TODO: Add tests for tool registration once implemented (Step 5)
# TODO: Add tests for agent behavior (LLM calls, tool usage) once tools are implemented 