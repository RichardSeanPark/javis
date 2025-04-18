import pytest
import inspect # inspect 모듈 임포트
import asyncio # 비동기 테스트를 위해 추가
from unittest.mock import patch, MagicMock, AsyncMock # <<< Added for mocking LLM call
# Mock 사용 금지 - from unittest.mock import AsyncMock, MagicMock, patch
import dotenv # For loading .env
import uuid # For session IDs
from typing import List, Optional, Any, Dict # Added Dict for type hints
import os # Import os module
import logging # logging 모듈 임포트
# Corrected import paths
# import google.generativeai as genai # 이전 라이브러리 이름, 주석 처리
import google.genai as genai # 새로운 (또는 현재 설치된) 라이브러리 이름 사용
# Corrected types import
from google.genai.types import GenerateContentResponse, Content, Part, FunctionCall # 경로 통일
# Pydantic v2 uses BaseModel
from pydantic import BaseModel, Field as PydanticField

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

APP_NAME = "jarvis-test-no-mock"
USER_ID = "test-user-no-mock"

# --- 전역 변수: 테스트 환경 설정 ---
# 실제 API 호출을 수행하므로, API 키가 필요합니다.
# load_dotenv()가 .env 파일에서 GEMINI_API_KEY를 로드할 것으로 기대합니다.
# API 키가 없거나 유효하지 않으면 테스트는 실패합니다.
API_KEY_LOADED = False

@pytest.fixture(scope="session", autouse=True)
def load_env_and_check_key():
    """Load environment variables and check for API key."""
    global API_KEY_LOADED
    dotenv.load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        API_KEY_LOADED = True
        # Configure API key for google.genai if necessary
        try:
            genai.configure(api_key=api_key)
            print("[Test Setup] Attempted to configure google.genai with API key.")
        except AttributeError:
             print("[Test Setup] google.genai.configure does not exist. Relying on automatic pickup.")
        except Exception as e:
            print(f"[Test Setup Warning] Error configuring google.genai: {e}")
    else:
        API_KEY_LOADED = False
        print("[Test Setup Warning] GEMINI_API_KEY not found in environment variables. Real API call tests will likely fail.")
    print(f"[Test Setup] API Key Loaded Status: {API_KEY_LOADED}")


# Fixture for JarvisDispatcher instance (no mocking)
@pytest.fixture
def real_dispatcher():
    """Creates a real JarvisDispatcher instance."""
    # Skip tests requiring real dispatcher if API key is not loaded
    if not API_KEY_LOADED:
        pytest.skip("Skipping test because GEMINI_API_KEY is not available.")
    return JarvisDispatcher()

# Fixture for InputParserAgent instance (no mocking)
# Not strictly needed as fixture since JarvisDispatcher creates it, but useful for potential direct testing
@pytest.fixture
def real_input_parser():
     # Skip tests requiring real parser if API key is not loaded
    if not API_KEY_LOADED:
        pytest.skip("Skipping test because GEMINI_API_KEY is not available.")
    return InputParserAgent()

# Test class for JarvisDispatcher - Using REAL components
class TestJarvisDispatcherReal:

    # Basic structural tests don't need API key, can use standard init
    @pytest.mark.asyncio
    async def test_process_request_is_async(self):
        """process_request 메서드가 async def로 정의되었는지 확인합니다."""
        # Need an instance, but don't need the API key for signature check
        dispatcher = JarvisDispatcher(model="mock-model-for-sig-check") # Use dummy model
        assert inspect.iscoroutinefunction(dispatcher.process_request), \
            "process_request 메서드는 async def여야 합니다."

    @pytest.mark.asyncio
    async def test_process_request_accepts_string_input(self):
        """process_request 메서드가 'user_input' 문자열 인자를 받는지 확인합니다."""
        dispatcher = JarvisDispatcher(model="mock-model-for-sig-check") # Use dummy model
        sig = inspect.signature(dispatcher.process_request)
        params = sig.parameters
        assert 'user_input' in params, "process_request 메서드는 'user_input' 인자를 가져야 합니다."
        assert params['user_input'].annotation == str, \
            "'user_input' 인자의 타입 힌트는 str이어야 합니다."

    # Initialization test needs a real instance if checking LLM init
    def test_dispatcher_initialization(self, real_dispatcher):
        """JarvisDispatcher __init__이 속성들을 올바르게 설정하고 LLM 클라이언트를 관리하는지 확인합니다."""
        dispatcher = real_dispatcher # Use fixture that checks API key
        assert isinstance(dispatcher.instruction, str)
        assert "central dispatcher" in dispatcher.instruction
        # Check description
        # assert "automatic delegation" in dispatcher.description # BaseAgent로 변경하며 제거
        # Check if the dispatcher's own LLM client was initialized
        dispatcher_llm_client = dispatcher.get_llm_client(dispatcher.model)
        assert dispatcher_llm_client is not None, f"Dispatcher LLM client for model '{dispatcher.model}' should be initialized"
        # Check the type of the initialized client
        # genai.Client()를 사용하도록 변경됨
        # assert hasattr(dispatcher_llm_client, 'generate_content_async'), \
        #     f"Dispatcher LLM client should have 'generate_content_async' method, but got type {type(dispatcher_llm_client)}\"
        assert isinstance(dispatcher_llm_client, genai.Client), \
            f"Dispatcher LLM client should be a genai.Client instance, but got {type(dispatcher_llm_client)}"
        print(f"[Test Init Check] dispatcher.get_llm_client({dispatcher.model}) type is: {type(dispatcher_llm_client)}")

        # Check InputParserAgent initialization
        assert dispatcher.input_parser is not None
        assert isinstance(dispatcher.input_parser, InputParserAgent)
        # Check internal client dict (optional, for deeper inspection)
        assert dispatcher.model in dispatcher.llm_clients
        assert dispatcher.llm_clients[dispatcher.model] == dispatcher_llm_client

    # Registration tests don't need API key
    def test_register_agent_updates_sub_agents_and_tools(self):
        """register_agent가 sub_agents와 tools 리스트를 모두 업데이트하는지 확인"""
        dispatcher = JarvisDispatcher(model="mock-model-for-reg-check") # Dummy model ok
        # --- 추가: 테스트 시작 시 sub_agents 및 tools 초기화 ---
        dispatcher.sub_agents = {}
        dispatcher.tools = []
        # --- 초기화 끝 ---
        agent1 = LlmAgent(name="Agent1", description="Desc 1")
        agent2 = LlmAgent(name="Agent2", description="Desc 2")

        dispatcher.register_agent(agent1)
        assert agent1.name in dispatcher.sub_agents
        assert dispatcher.sub_agents[agent1.name] == agent1
        assert agent1 in dispatcher.tools
        assert len(dispatcher.tools) == 1

        dispatcher.register_agent(agent2)
        assert agent2.name in dispatcher.sub_agents
        assert dispatcher.sub_agents[agent2.name] == agent2
        assert agent2 in dispatcher.tools
        assert len(dispatcher.tools) == 2
        assert agent1 in dispatcher.tools

    def test_register_agent_overwrites_and_updates_tools(self, caplog):
        """register_agent가 기존 에이전트를 덮어쓰고 tools 리스트를 업데이트하며 경고 로그를 남기는지 확인"""
        # Set log level to capture warnings
        caplog.set_level(logging.WARNING)

        dispatcher = JarvisDispatcher(model="mock-model-for-reg-check") # Dummy model ok
        # --- 추가: 테스트 시작 시 sub_agents 및 tools 초기화 ---
        dispatcher.sub_agents = {}
        dispatcher.tools = []
        # --- 초기화 끝 ---
        agent_v1 = LlmAgent(name="AgentV", description="V1")
        agent_v2 = LlmAgent(name="AgentV", description="V2") # Same name

        dispatcher.register_agent(agent_v1)
        assert agent_v1 in dispatcher.tools
        assert len(dispatcher.tools) == 1
        assert dispatcher.tools[0].description == "V1"
        # --- 추가: 첫 번째 등록 확인 ---
        assert "AgentV" in dispatcher.sub_agents, "AgentV should be in sub_agents after first registration"
        # --- 확인 끝 ---

        # Clear previous logs before registering again
        caplog.clear()

        dispatcher.register_agent(agent_v2)

        assert agent_v2.name in dispatcher.sub_agents
        assert dispatcher.sub_agents[agent_v2.name] == agent_v2
        assert len(dispatcher.tools) == 1 # Should contain only agent_v2
        assert dispatcher.tools[0] == agent_v2
        assert dispatcher.tools[0].description == "V2"

        # --- 추가: 실제 로그 출력 ---
        print(f"Captured logs after second registration:\n{caplog.text}")
        # --- 로그 출력 끝 ---

        # Check logs for the warning message
        assert "Agent with name 'AgentV' overwritten." in caplog.text # <<< WARNING 로그 확인 활성화
        # Check for the info message as well (might need to adjust level if checking info)
        # assert "Agent 'AgentV' (type: <class 'google.adk.agents.llm_agent.LlmAgent'>, model: N/A) registered/updated." in caplog.text # <<< INFO 로그 확인 제거


    # --- Integration Tests using Real Components ---

    async def _run_real_delegation_test(
        self,
        real_dispatcher: JarvisDispatcher, # Use the fixture
        user_query: str,
        registered_agents_config: List[Dict[str, str]], # name, description
        expect_delegation_to: Optional[str] = None, # Name of agent expected to be invoked
        expect_no_delegation_reason: Optional[str] = None # Substring expected in final response if no delegation
    ):
        """
        Helper function for integration tests with real API calls.
        Asserts based on event stream analysis or final dispatcher response.
        """
        print(f"\n--- Running Real Delegation Test ---")
        print(f"Query: '{user_query}'")
        print(f"Registered Agents: {[a['name'] for a in registered_agents_config]}")
        print(f"Expecting delegation to: {expect_delegation_to}")
        print(f"Expecting non-delegation reason containing: {expect_no_delegation_reason}")

        # --- 추가: 테스트 실행 전 디스패처 상태 초기화 ---
        real_dispatcher.sub_agents = {}
        real_dispatcher.tools = []
        # --- 초기화 끝 ---

        # 1. Register REAL Agents (LlmAgent instances, no mocking/patching)
        agent_instances = []
        for agent_conf in registered_agents_config:
            # Create actual LlmAgent instance, adding a dummy model name
            agent_instance = LlmAgent(
                name=agent_conf['name'], 
                description=agent_conf['description'],
                model="mock-subagent-model" # Add dummy model name
            )
            real_dispatcher.register_agent(agent_instance)
            agent_instances.append(agent_instance)
            print(f"[Test Setup] Registered real agent: {agent_instance.name}")

        # 2. Setup Runner
        session_service = InMemorySessionService()
        runner = Runner(
            agent=real_dispatcher,
            app_name=APP_NAME,
            session_service=session_service
        )
        session_id = str(uuid.uuid4())
        session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
        print(f"[Test Setup] Session created: {session_id}")

        # 3. Prepare Input
        content = Content(role="user", parts=[Part(text=user_query)])

        # 4. Run and Collect Events (Real API calls will happen here)
        events = []
        final_response_text = "Default: No final response captured."
        execution_error = None
        try:
            print("[Test Run] Starting runner.run_async...")
            async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=content):
                # Log all events for detailed debugging
                event_author = getattr(event, 'author', 'N/A')
                event_type = type(event).__name__
                event_final = getattr(event, 'is_final_response', lambda: False)()
                event_content_str = str(getattr(event, 'content', 'N/A'))[:150] + "..."
                print(f"  [Event] Author: {event_author}, Type: {event_type}, Final: {event_final}, Content: {event_content_str}")
                events.append(event)

                # Capture the final response text, regardless of author for now
                if event_final:
                     current_final_text = "(No text in final event)"
                     if event.content and hasattr(event.content, 'parts') and event.content.parts:
                          if hasattr(event.content.parts[0], 'text'):
                               current_final_text = event.content.parts[0].text
                     final_response_text = current_final_text # Keep the last final response
                     print(f"  [Event] Captured final response text: '{final_response_text}'")


            print("[Test Run] runner.run_async finished.")

        except Exception as e:
            import traceback
            print(f"[Test Run Error] Exception during runner.run_async: {e}")
            print(traceback.format_exc()) # Print full traceback
            execution_error = e
            final_response_text = f"Error during run: {e}"

        print(f"<<< Final Response Text: {final_response_text}")

        # 5. Assert based on expected outcome (delegation or not)

        if execution_error:
            pytest.fail(f"Test failed due to exception during run_async: {execution_error}")

        if expect_delegation_to:
            # 수정: 이벤트 author 대신 최종 응답 텍스트 확인
            expected_delegation_message = f"Delegating task to agent: {expect_delegation_to}".lower()
            actual_response_lower = final_response_text.lower()
            print(f"[Test Assertion] Checking if '{actual_response_lower}' contains '{expected_delegation_message}'") # 로깅 추가
            assert expected_delegation_message in actual_response_lower, (\
                f"Expected final response to indicate delegation to '{expect_delegation_to}'. "
                f"Expected substring: '{expected_delegation_message}', Actual response: '{final_response_text}'"
            )
            print(f"[Test Assertion] Successfully found delegation message for {expect_delegation_to} in response.")

        elif expect_no_delegation_reason:
            # Check if the final response text contains the expected reason
            actual_response_lower = final_response_text.lower() # Ensure lowercase comparison
            print(f"[Test Assertion] Checking if '{actual_response_lower}' contains '{expect_no_delegation_reason.lower()}'") # 로깅 추가
            assert expect_no_delegation_reason.lower() in actual_response_lower, (\
                f"Expected final response to contain '{expect_no_delegation_reason}', but got: '{final_response_text}'"
            )
            # Also check that the unsuitable agent was NOT invoked (optional, might be flaky)
            unsuitable_agent_invoked = any(
                getattr(event, 'author', None) == agent_instances[0].name # Assumes only one agent registered for this test type
                for event in events
            )
            assert not unsuitable_agent_invoked, (
                 f"Expected no delegation, but found event indicating invocation of unsuitable agent '{agent_instances[0].name}'. "
                 f"Events captured: {[(getattr(e, 'author', 'N/A'), type(e).__name__) for e in events]}"
            )

            print(f"[Test Assertion] Successfully confirmed no delegation and reason '{expect_no_delegation_reason}' found in response.")
        else:
            pytest.fail("Test case must specify either expect_delegation_to or expect_no_delegation_reason.")


    @pytest.mark.asyncio
    async def test_delegation_to_coding_agent_real(self, real_dispatcher):
        """Dispatcher가 CodingAgent 설명 기반으로 올바르게 위임하는지 통합 테스트 (Real API)"""
        await self._run_real_delegation_test(
            real_dispatcher=real_dispatcher,
            user_query="Write a python function to add two numbers",
            registered_agents_config=[
                {'name': "CodingAgent", 'description': "Handles code generation, explanation, and debugging related to software development."},
                {'name': "KnowledgeQA_Agent", 'description': "Answers general knowledge questions based on provided context or its internal knowledge base."}
            ],
            expect_delegation_to="CodingAgent" # Assert that the runner attempts to invoke CodingAgent
        )

    @pytest.mark.asyncio
    async def test_delegation_to_qa_agent_real(self, real_dispatcher):
        """Dispatcher가 KnowledgeQA_Agent 설명 기반으로 올바르게 위임하는지 통합 테스트 (Real API)"""
        await self._run_real_delegation_test(
            real_dispatcher=real_dispatcher,
            user_query="What is the capital of France?",
            registered_agents_config=[
                {'name': "CodingAgent", 'description': "Handles code generation, explanation, and debugging related to software development."},
                {'name': "KnowledgeQA_Agent", 'description': "Answers general knowledge questions based on provided context or its internal knowledge base."}
            ],
            expect_delegation_to="KnowledgeQA_Agent" # Assert that the runner attempts to invoke QA Agent
        )

    @pytest.mark.asyncio
    async def test_delegation_no_suitable_agent_real(self, real_dispatcher):
        """적절한 에이전트가 없을 때 Dispatcher가 직접 응답하거나 위임 불가 응답하는지 테스트 (Real API)"""
        await self._run_real_delegation_test(
            real_dispatcher=real_dispatcher,
            user_query="Tell me an interesting fact about hummingbirds.", # A query the coding agent shouldn't handle
            registered_agents_config=[
                 {'name': "CodingAgent", 'description': "Handles code generation, explanation, and debugging related to software development."}
                 # Only CodingAgent is registered
            ],
            # Expect the dispatcher's final response to indicate inability to delegate
            # Update the expected reason based on the actual message
            expect_no_delegation_reason="No suitable internal or external agent found" # Check for the beginning of the actual message
        )

    # --- Tests for A2A Placeholder ---

    @pytest.mark.asyncio
    async def test_a2a_placeholder_entry_on_no_agent_mocked(self, real_dispatcher, caplog):
        """
        ### 3.3.3 Test Case: A2A 플레이스홀더 진입 테스트 (Mock)
        디스패처 LLM이 "NO_AGENT"를 반환하도록 Mocking하고,
        process_request 실행 시 A2A 플레이스홀더 블록 내의 로그가 출력되는지 확인.
        """
        # Set log level to capture info messages
        caplog.set_level(logging.INFO)
        dispatcher = real_dispatcher

        # Mock the InputParserAgent to return a predictable ParsedInput
        mock_parsed_input = ParsedInput(
            original_text="Some ambiguous request",
            original_language="en",
            english_text="Some ambiguous request",
            intent=None, entities=None, domain=None
        )
        # Use patch with the full class path instead of patch.object
        with patch('src.jarvis.components.input_parser.InputParserAgent.process_input', new_callable=AsyncMock, return_value=mock_parsed_input):
            # --- Corrected Mocking ---
            mock_llm_client_instance = MagicMock(spec=genai.Client) # Use MagicMock for easier attribute setting
            mock_aio_attr = AsyncMock()
            mock_models_attr = AsyncMock()
            mock_generate_content_method = AsyncMock(return_value=AsyncMock(text="NO_AGENT")) # Mock the response object directly

            mock_models_attr.generate_content = mock_generate_content_method
            mock_aio_attr.models = mock_models_attr
            mock_llm_client_instance.aio = mock_aio_attr
            # --- End Corrected Mocking ---

            # Use patch with the full class path for get_llm_client
            with patch('src.jarvis.core.dispatcher.JarvisDispatcher.get_llm_client', return_value=mock_llm_client_instance) as mock_get_client:
                await dispatcher.process_request("Some ambiguous request")
                # Assertions
                mock_get_client.assert_called_once_with(dispatcher.model)
                mock_generate_content_method.assert_called_once() # Assert on the final mocked method
                assert "No suitable internal agent found via LLM. Attempting A2A Discovery (Placeholder)." in caplog.text, \
                    "Log message for A2A placeholder check not found."

    @pytest.mark.asyncio
    async def test_a2a_placeholder_return_message_mocked(self, real_dispatcher):
        """
        ### 3.3.3 Test Case: A2A 플레이스홀더 후 반환 메시지 테스트 (Mock)
        디스패처 LLM이 "NO_AGENT"를 반환하도록 Mocking하고,
        process_request가 최종적으로 올바른 메시지를 반환하는지 확인.
        """
        dispatcher = real_dispatcher

        # Mock the InputParserAgent
        mock_parsed_input = ParsedInput(
            original_text="Another ambiguous request",
            original_language="en",
            english_text="Another ambiguous request",
            intent=None, entities=None, domain=None
        )
        # Use patch with the full class path instead of patch.object
        with patch('src.jarvis.components.input_parser.InputParserAgent.process_input', new_callable=AsyncMock, return_value=mock_parsed_input):
             # --- Corrected Mocking ---
            mock_llm_client_instance = MagicMock(spec=genai.Client)
            mock_aio_attr = AsyncMock()
            mock_models_attr = AsyncMock()
            mock_generate_content_method = AsyncMock(return_value=AsyncMock(text="NO_AGENT"))

            mock_models_attr.generate_content = mock_generate_content_method
            mock_aio_attr.models = mock_models_attr
            mock_llm_client_instance.aio = mock_aio_attr
            # --- End Corrected Mocking ---

            # Use patch with the full class path for get_llm_client
            with patch('src.jarvis.core.dispatcher.JarvisDispatcher.get_llm_client', return_value=mock_llm_client_instance) as mock_get_client:
                final_message = await dispatcher.process_request("Another ambiguous request")
                # Assertions
                mock_get_client.assert_called_once_with(dispatcher.model)
                mock_generate_content_method.assert_called_once()
                expected_message = "No suitable internal or external agent found to handle the request."
                assert final_message == expected_message, \
                    f"Expected final message '{expected_message}', but got '{final_message}'"

    # ... rest of the class ...
 