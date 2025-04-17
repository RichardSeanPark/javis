import pytest
import inspect # inspect 모듈 임포트
import asyncio # 비동기 테스트를 위해 추가
from unittest.mock import AsyncMock, MagicMock, patch # patch 추가
import dotenv # For loading .env
import uuid # For session IDs
from typing import List, Optional, Any # Added for type hints

# google.ai.generativelanguage에서 임포트 시도 (제거)
# from google.ai.generativelanguage import Content, Part
# GenerateContentResponse는 google.generativeai.types 에 있을 가능성 높음 (제거)
# from google.generativeai.types import GenerateContentResponse 

# 새로운 google-genai SDK 경로 시도
from google.genai.types import Content, Part, GenerateContentResponse

from google.adk.runners import Runner # ADK Runner (InMemoryRunner -> Runner로 변경)
# SessionService 임포트 경로 및 이름 수정 (0.1.0 기준)
from google.adk.memory import InMemoryMemoryService # Session service (Import Correct Name)
# google.adk.sessions 모듈에서 InMemorySessionService 임포트 시도
from google.adk.sessions import InMemorySessionService 
from google.adk.agents import LlmAgent, Agent # LlmAgent, Agent 임포트
from google.adk.agents.invocation_context import InvocationContext # Check this import path

from src.jarvis.core.dispatcher import JarvisDispatcher
from src.jarvis.components.input_parser import InputParserAgent # 필요한 경우 임포트
from src.jarvis.models.input import ParsedInput # ParsedInput 임포트

APP_NAME = "jarvis-test"
USER_ID = "test-user"

@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load environment variables from .env file for the test session."""
    dotenv.load_dotenv()

# Fixture for JarvisDispatcher instance (if needed later)
@pytest.fixture
def dispatcher():
    """JarvisDispatcher 인스턴스를 생성하는 fixture"""
    return JarvisDispatcher()

# Fixture for mocking InputParserAgent.process_input
@pytest.fixture
def mock_input_parser(mocker):
    """InputParserAgent.process_input을 모킹하는 fixture"""
    # InputParserAgent의 인스턴스 생성 또는 모킹
    mock_parser_instance = MagicMock(spec=InputParserAgent)
    # process_input 메서드를 AsyncMock으로 모킹
    mock_parser_instance.process_input = AsyncMock(return_value=MagicMock(spec=ParsedInput))
    
    # JarvisDispatcher가 InputParserAgent를 인스턴스화할 때 이 mock 객체를 사용하도록 패치
    mocker.patch('src.jarvis.core.dispatcher.InputParserAgent', return_value=mock_parser_instance)
    return mock_parser_instance

# Mock Agent 클래스 정의 - 호출 시 식별자 반환하도록 수정
class MockAgent(LlmAgent):
    def __init__(self, name="MockAgent", description="A mock agent.", model="mock-model"):
        # LlmAgent의 __init__을 호출. model='mock-model' 전달
        super().__init__(name=name, description=description, model=model)

        # LlmAgent 초기화 후 self.llm 속성 확인 및 모킹
        # LlmAgent.__init__이 model 인자를 기반으로 self.llm을 설정할 것으로 기대.
        # 만약 설정하지 않았거나, 테스트 환경에서 모킹이 필요한 경우 MagicMock 할당.
        if not hasattr(self, 'llm') or self.llm is None:
            # Pydantic 모델 초기화 후 속성 추가 시도
            # model_config['extra'] = 'allow' 가 아니면 실패할 수 있음.
            # LlmAgent의 기본 설정에 따라 달라짐.
            try:
                # 직접 할당 시도
                object.__setattr__(self, 'llm', MagicMock()) # Use object.__setattr__ to bypass Pydantic validation temporarily if needed
                print(f"[MockAgent Debug] Assigned MagicMock to self.llm for {name}")
            except Exception as e:
                print(f"[MockAgent Debug] Failed to assign MagicMock to self.llm for {name}: {e}")
                # 할당 실패 시에도 테스트 진행을 위해 임시 객체 설정 시도 (덜 안전)
                # self._temp_llm = MagicMock()
                # self.llm = self._temp_llm
        else:
            print(f"[MockAgent Debug] self.llm already exists for {name}. Type: {type(self.llm)}")

        # self.llm이 MagicMock 또는 실제 LLM 클라이언트 Mock일 수 있음
        # generate_content_async 메서드가 있는지 확인하고 없으면 추가
        current_llm = getattr(self, 'llm', None)
        if current_llm and not hasattr(current_llm, 'generate_content_async'):
            current_llm.generate_content_async = AsyncMock(return_value=MagicMock(spec=GenerateContentResponse))
            print(f"[MockAgent Debug] Added generate_content_async mock to self.llm for {name}")
        elif current_llm:
            # 이미 메서드가 있다면 (예: 실제 LLM 클라이언트 Mock), 해당 메서드를 AsyncMock으로 덮어씀
            current_llm.generate_content_async = AsyncMock(return_value=MagicMock(spec=GenerateContentResponse))
            print(f"[MockAgent Debug] Overwrote generate_content_async mock for self.llm for {name}")
        else:
             print(f"[MockAgent Debug] self.llm is still None or missing for {name}, cannot mock generate_content_async")


        # ADK가 __call__ 대신 invoke를 호출할 수 있으므로 invoke에 로직 집중
        self._response_text = f"Response from {self.name}"

    async def __call__(self, input_text: str) -> str:
        """Simulate agent invocation, return identifier."""
        print(f"MockAgent '{self.name}' __call__ invoked with: {input_text[:50]}...")
        return self._response_text

    # ADK Runner가 invoke를 호출할 수 있으므로 invoke도 구현 (async 필요)
    async def invoke(self, ctx: InvocationContext) -> None:
        print(f"MockAgent '{self.name}' invoked via Runner")
        last_message = ctx.history.get_last_message()
        input_text = last_message.content.parts[0].text if last_message and last_message.content else ""
        print(f"MockAgent '{self.name}' received input: {input_text[:50]}...")
        # __call__ 대신 직접 응답 설정
        ctx.set_agent_response(self._response_text)


# Test class for JarvisDispatcher
class TestJarvisDispatcher:

    @pytest.mark.asyncio # 개별 메서드에 asyncio 마크 추가
    async def test_process_request_is_async(self, dispatcher):
        """process_request 메서드가 async def로 정의되었는지 확인합니다."""
        assert inspect.iscoroutinefunction(dispatcher.process_request), \
            "process_request 메서드는 async def여야 합니다."

    @pytest.mark.asyncio # 개별 메서드에 asyncio 마크 추가
    async def test_process_request_accepts_string_input(self, dispatcher):
        """process_request 메서드가 'user_input' 문자열 인자를 받는지 확인합니다."""
        sig = inspect.signature(dispatcher.process_request)
        params = sig.parameters
        assert 'user_input' in params, "process_request 메서드는 'user_input' 인자를 가져야 합니다."
        assert params['user_input'].annotation == str, \
            "'user_input' 인자의 타입 힌트는 str이어야 합니다."

    def test_dispatcher_initialization_sets_instruction(self):
        """JarvisDispatcher __init__이 instruction을 올바르게 설정하는지 확인"""
        dispatcher = JarvisDispatcher()
        assert isinstance(dispatcher.instruction, str)
        assert "central dispatcher" in dispatcher.instruction
        assert "delegate it to the most suitable specialized agent" in dispatcher.instruction
        assert "tools" in dispatcher.instruction # Check for keywords
        # Check description is also updated
        assert "automatic delegation" in dispatcher.description

    def test_register_agent_updates_sub_agents_and_tools(self, mocker):
        """register_agent가 sub_agents와 tools 리스트를 모두 업데이트하는지 확인"""
        dispatcher = JarvisDispatcher()
        agent1 = MockAgent(name="Agent1")
        agent2 = MockAgent(name="Agent2")

        dispatcher.register_agent(agent1)
        assert agent1.name in dispatcher.sub_agents
        assert dispatcher.sub_agents[agent1.name] == agent1
        assert agent1 in dispatcher.tools # Verify added to tools
        assert len(dispatcher.tools) == 1

        dispatcher.register_agent(agent2)
        assert agent2.name in dispatcher.sub_agents
        assert dispatcher.sub_agents[agent2.name] == agent2
        assert agent2 in dispatcher.tools # Verify added to tools
        assert len(dispatcher.tools) == 2 # Verify count incremented
        assert agent1 in dispatcher.tools # Verify agent1 still present

    def test_register_agent_overwrites_and_updates_tools(self, mocker):
        """register_agent가 기존 에이전트를 덮어쓰고 tools 리스트를 업데이트하는지 확인"""
        dispatcher = JarvisDispatcher()
        agent_v1 = MockAgent(name="AgentV")
        agent_v2 = MockAgent(name="AgentV") # Same name

        dispatcher.register_agent(agent_v1)
        assert agent_v1 in dispatcher.tools
        assert len(dispatcher.tools) == 1
        assert dispatcher.tools[0].name == "AgentV"

        with patch('builtins.print') as mock_print:
            dispatcher.register_agent(agent_v2)

        assert agent_v2.name in dispatcher.sub_agents
        assert dispatcher.sub_agents[agent_v2.name] == agent_v2 # Overwritten in dict
        assert len(dispatcher.tools) == 1       # Check tools length is correct
        assert dispatcher.tools[0] == agent_v2  # Check v2 added to tools
        assert dispatcher.tools[0].name == "AgentV" # Check v2 name
        # Check print warning
        mock_print.assert_any_call("Warning: Agent with name 'AgentV' already registered. Overwriting.")
        mock_print.assert_any_call("Agent 'AgentV' registered and added to tools list for ADK delegation.")

    @pytest.mark.asyncio # 개별 메서드에 asyncio 마크 추가
    async def test_process_request_calls_input_parser(self, mocker):
        """process_request가 self.input_parser.process_input을 호출하고 결과를 저장하는지 확인합니다."""
        # Arrange
        mock_parsed_input = MagicMock(spec=ParsedInput)
        mock_parsed_input.original_language = 'ko'
        mock_parsed_input.intent = None
        mock_parsed_input.domain = None
        mock_parsed_input.english_text = "Mocked english input for test"
        mock_process_input = AsyncMock(return_value=mock_parsed_input)
        mocker.patch.object(InputParserAgent, 'process_input', new=mock_process_input)

        # Dispatcher 인스턴스 생성
        dispatcher_instance = JarvisDispatcher()
        # mocker.patch.object를 사용하여 llm 객체와 그 메서드를 모킹
        mock_llm = MagicMock()
        mock_llm.generate_content_async = AsyncMock(return_value=MagicMock(spec=GenerateContentResponse))
        mocker.patch.object(dispatcher_instance, 'llm', mock_llm)

        test_input = "테스트 입력"

        # Act
        await dispatcher_instance.process_request(test_input)

        # Assert
        mock_process_input.assert_awaited_once_with(test_input)
        assert dispatcher_instance.current_parsed_input == mock_parsed_input
        assert dispatcher_instance.current_original_language == 'ko'
        # llm 호출 여부 확인
        mock_llm.generate_content_async.assert_awaited_once()

    @pytest.mark.asyncio # 개별 메서드에 asyncio 마크 추가
    async def test_process_request_calls_llm_with_tools_for_delegation(self, mocker):
        """process_request가 self.llm.generate_content_async를 tools와 함께 호출하는지 확인"""
        # Arrange
        mock_parsed_input = MagicMock(spec=ParsedInput)
        mock_parsed_input.intent = 'some_intent'
        mock_parsed_input.domain = 'some_domain'
        mock_parsed_input.original_language = 'en'
        mock_parsed_input.english_text = "User query in English"
        mocker.patch.object(InputParserAgent, 'process_input', return_value=mock_parsed_input)

        dispatcher = JarvisDispatcher()
        agent1 = MockAgent(name="Agent1")
        agent2 = MockAgent(name="Agent2")
        dispatcher.register_agent(agent1)
        dispatcher.register_agent(agent2)
        actual_tools_list = dispatcher.tools

        # mocker.patch.object를 사용하여 llm 객체와 그 메서드를 모킹
        mock_llm = MagicMock()
        mock_llm.generate_content_async = AsyncMock(return_value=MagicMock(spec=GenerateContentResponse))
        mocker.patch.object(dispatcher, 'llm', mock_llm)

        # Act
        await dispatcher.process_request("Original user input")

        # Assert
        mock_llm.generate_content_async.assert_awaited_once_with(
            mock_parsed_input.english_text,
            tools=actual_tools_list
        )
        assert len(actual_tools_list) == 2
        assert agent1 in actual_tools_list
        assert agent2 in actual_tools_list

    # --- End-to-End Delegation Tests using InMemoryRunner --- # 이 섹션은 이제 변경됩니다.

    @pytest.mark.asyncio
    async def test_delegation_to_coding_agent_live(self, mocker):
        """Dispatcher가 CodingAgent로 위임하기 위해 LLM을 올바르게 호출하는지 테스트"""
        # Arrange
        user_query = "Write a python function to add two numbers"
        mock_english_text = "Write a python function to add two numbers"
        mock_parsed_input = MagicMock(spec=ParsedInput)
        mock_parsed_input.original_language = 'en'
        mock_parsed_input.english_text = mock_english_text
        mock_parsed_input.intent = 'code_generation' # 필요시 유지
        mock_parsed_input.domain = 'coding' # 필요시 유지
        mocker.patch.object(InputParserAgent, 'process_input', AsyncMock(return_value=mock_parsed_input))

        dispatcher = JarvisDispatcher()
        coding_agent = MockAgent(name="CodingAgent", description="Handles code generation, explanation, and debugging.")
        qa_agent = MockAgent(name="KnowledgeQA_Agent", description="Answers general knowledge questions.")
        dispatcher.register_agent(coding_agent)
        dispatcher.register_agent(qa_agent)

        # Mock dispatcher.llm.generate_content_async
        mock_llm = MagicMock()
        mock_llm.generate_content_async = AsyncMock(return_value=MagicMock(spec=GenerateContentResponse))
        mocker.patch.object(dispatcher, 'llm', mock_llm)

        # Act
        await dispatcher.process_request(user_query)

        # Assert
        # LLM 호출이 올바른 english_text와 등록된 tools 리스트로 이루어졌는지 확인
        mock_llm.generate_content_async.assert_awaited_once_with(
            mock_english_text, # 파서에서 반환된 영어 텍스트
            tools=dispatcher.tools # 등록된 에이전트 목록
        )
        assert len(dispatcher.tools) == 2
        assert coding_agent in dispatcher.tools
        assert qa_agent in dispatcher.tools

    @pytest.mark.asyncio
    async def test_delegation_to_qa_agent_live(self, mocker):
        """Dispatcher가 KnowledgeQA_Agent로 위임하기 위해 LLM을 올바르게 호출하는지 테스트"""
        # Arrange
        user_query = "What is the capital of France?"
        mock_english_text = "What is the capital of France?"
        mock_parsed_input = MagicMock(spec=ParsedInput)
        mock_parsed_input.original_language = 'en'
        mock_parsed_input.english_text = mock_english_text
        mock_parsed_input.intent = 'question_answering'
        mock_parsed_input.domain = 'general'
        mocker.patch.object(InputParserAgent, 'process_input', AsyncMock(return_value=mock_parsed_input))

        dispatcher = JarvisDispatcher()
        coding_agent = MockAgent(name="CodingAgent", description="Handles code generation, explanation, and debugging.")
        qa_agent = MockAgent(name="KnowledgeQA_Agent", description="Answers general knowledge questions.")
        dispatcher.register_agent(coding_agent)
        dispatcher.register_agent(qa_agent)

        # Mock dispatcher.llm.generate_content_async
        mock_llm = MagicMock()
        mock_llm.generate_content_async = AsyncMock(return_value=MagicMock(spec=GenerateContentResponse))
        mocker.patch.object(dispatcher, 'llm', mock_llm)

        # Act
        await dispatcher.process_request(user_query)

        # Assert
        mock_llm.generate_content_async.assert_awaited_once_with(
            mock_english_text,
            tools=dispatcher.tools
        )
        assert len(dispatcher.tools) == 2
        assert coding_agent in dispatcher.tools
        assert qa_agent in dispatcher.tools

    @pytest.mark.asyncio
    async def test_delegation_no_suitable_agent_live(self, mocker):
        """적절한 에이전트가 없을 때 Dispatcher가 LLM을 올바르게 호출하는지 테스트"""
        # Arrange
        user_query = "Tell me a joke"
        mock_english_text = "Tell me a joke"
        mock_parsed_input = MagicMock(spec=ParsedInput)
        mock_parsed_input.original_language = 'en'
        mock_parsed_input.english_text = mock_english_text
        mock_parsed_input.intent = 'chit_chat'
        mock_parsed_input.domain = 'general'
        mocker.patch.object(InputParserAgent, 'process_input', AsyncMock(return_value=mock_parsed_input))

        dispatcher = JarvisDispatcher()
        # 특정 에이전트만 등록 (예: 코딩 에이전트)
        coding_agent = MockAgent(name="CodingAgent", description="Handles code generation, explanation, and debugging.")
        dispatcher.register_agent(coding_agent)

        # Mock dispatcher.llm.generate_content_async
        mock_llm = MagicMock()
        mock_llm.generate_content_async = AsyncMock(return_value=MagicMock(spec=GenerateContentResponse))
        mocker.patch.object(dispatcher, 'llm', mock_llm)

        # Act
        await dispatcher.process_request(user_query)

        # Assert
        # LLM 호출이 이루어졌는지, 그리고 tools 목록에 코딩 에이전트만 포함되었는지 확인
        mock_llm.generate_content_async.assert_awaited_once_with(
            mock_english_text,
            tools=dispatcher.tools
        )
        assert len(dispatcher.tools) == 1
        assert coding_agent in dispatcher.tools
 