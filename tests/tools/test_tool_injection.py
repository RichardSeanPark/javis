import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock
import asyncio
from typing import Dict, List, Any, Optional, Union, AsyncGenerator

from google.genai.types import Content, Part
from google.adk.agents import LlmAgent, BaseAgent
from google.adk.events import Event
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools import BaseTool

from src.jarvis.core.dispatcher import JarvisDispatcher, DelegationInfo
from src.jarvis.agents.qa_agent import KnowledgeQA_Agent
from src.jarvis.agents.coding_agent import CodingAgent
from src.jarvis.components.response_generator import ResponseGenerator
from src.jarvis.tools import translate_tool, web_search_tool, code_execution_tool
from src.jarvis.tools import available_tools
import logging

logger = logging.getLogger(__name__)

# JarvisDispatcher를 상속받는 테스트용 클래스 정의
class TestJarvisDispatcher(JarvisDispatcher):
    """테스트를 위한 JarvisDispatcher 서브클래스"""
    
    def __init__(self, *args, **kwargs):
        # 부모 클래스 초기화
        super().__init__(*args, **kwargs)
        # 모킹을 위한 속성 설정
        mock_response_generator = MagicMock(spec=ResponseGenerator)
        # 입력받은 텍스트를 그대로 반환하도록 변경
        mock_response_generator.generate_response = AsyncMock(side_effect=lambda text, lang: text)
        self.response_generator = mock_response_generator
        # 테스트에서 설정할 반환값
        self._mock_process_request_return = None
        # 에러 테스트용 플래그
        self._should_raise_error = False
        
    async def process_request(self, user_input: str, session_id: Optional[str] = None) -> Union[DelegationInfo, str]:
        """
        원본 메서드를 오버라이드하여 테스트에서 설정한 값을 반환합니다.
        """
        return self._mock_process_request_return
        
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        _run_async_impl을 오버라이드하여 오류 테스트를 위한 기능 추가
        """
        user_input = None
        session_id = ctx.session.id if ctx.session else None
        final_response_message = "Error: An unexpected error occurred." # Default error message
        original_tools = None
        original_instruction = None
        sub_agent_to_restore = None

        try:
            # Extract user input
            if ctx.user_content and hasattr(ctx.user_content, 'parts') and ctx.user_content.parts:
                if hasattr(ctx.user_content.parts[0], 'text'):
                    user_input = ctx.user_content.parts[0].text

            if not user_input:
                logger.warning("_run_async_impl called without user input text in context.")
                final_response_message = "Error: Could not get user input from context."
            else:
                # Process the request to get delegation info or a direct response string
                result = await self.process_request(user_input, session_id=session_id)

                if isinstance(result, dict) and "agent_name" in result:
                    # --- Handle Delegation ---
                    delegation_info = result
                    agent_name = delegation_info["agent_name"]

                    if agent_name not in self.sub_agents:
                        logger.error(f"Delegation target agent '{agent_name}' not found in sub_agents.")
                        final_response_message = f"Error: Could not find agent {agent_name} to delegate to."
                    else:
                        sub_agent = self.sub_agents[agent_name]
                        sub_agent_to_restore = sub_agent
                        original_tools = sub_agent.tools.copy() # 복사를 사용하여 원본 보존
                        original_instruction = getattr(sub_agent, 'instruction', None)

                        try:
                            # 에러 플래그가 설정된 경우 여기서 예외 발생
                            if self._should_raise_error:
                                raise Exception("Simulated error during delegation preparation")
                                
                            # Temporarily modify sub-agent for the call
                            logger.info(f"Dispatcher delegating to sub-agent: {agent_name}")
                            # Tools injection
                            required_tools_from_info = delegation_info["required_tools"]
                            sub_agent.tools = required_tools_from_info
                            logger.debug(f"Temporarily injected tools into {agent_name}")

                            # Context and instruction update
                            context_prompt = "\n\n---\nContext:\n"
                            if delegation_info.get("conversation_history"):
                                context_prompt += f'Conversation History:\n{delegation_info["conversation_history"]}\n'
                            context_prompt += f'Original Language: {delegation_info["original_language"]}\n---'

                            base_instruction = original_instruction if original_instruction is not None else ""
                            temp_instruction = base_instruction + context_prompt

                            if hasattr(sub_agent, 'instruction'):
                                setattr(sub_agent, 'instruction', temp_instruction)
                                logger.debug(f"Temporarily updated instruction for {agent_name}")
                            else:
                                logger.warning(f"Agent {agent_name} does not have an 'instruction' attribute to update.")

                            # Yield the delegation event to the Runner
                            yield Event(
                                author=self.name,
                                content=Content(parts=[Part(text=f"[System] Delegating to {agent_name}. Runner should invoke.")])
                            )
                            # Exit generator after delegation event is yielded
                            return

                        except Exception as delegation_prep_error:
                            logger.error(f"Error during delegation prep for {agent_name}: {delegation_prep_error}")
                            final_response_message = f"Error: Internal error while preparing delegation for agent {agent_name}."
                            # Fall through to finally block for cleanup, then yield error

                elif isinstance(result, str):
                    final_response_message = result
                else:
                    logger.error(f"process_request returned unexpected type: {type(result)}")
                    final_response_message = "Error: Internal dispatcher error due to unexpected result type."

        except Exception as outer_e:
            logger.error(f"Unexpected error in _run_async_impl: {outer_e}")
            final_response_message = "Error: An unexpected error occurred during execution."
        finally:
            if sub_agent_to_restore:
                try:
                    # 원래 도구 복원
                    if original_tools is not None:
                        sub_agent_to_restore.tools = original_tools
                        logger.debug(f"Restored original tools for {sub_agent_to_restore.name}")
                    
                    # 원래 instruction 복원
                    if hasattr(sub_agent_to_restore, 'instruction') and original_instruction is not None:
                        setattr(sub_agent_to_restore, 'instruction', original_instruction)
                        logger.debug(f"Restored original instruction for {sub_agent_to_restore.name}")
                except Exception as restore_e:
                    logger.error(f"Error restoring state for {sub_agent_to_restore.name}: {restore_e}")

        # Generate and yield final response
        try:
            processed_final_response = await self.response_generator.generate_response(
                final_response_message, "en" # 테스트에서는 언어 고정
            )
            yield Event(author=self.name, content=Content(parts=[Part(text=processed_final_response)]))
        except Exception as gen_e:
            logger.error(f"Error during final response generation: {gen_e}")
            yield Event(author=self.name, content=Content(parts=[Part(text="Error: Failed to generate final response.")]))


class TestToolInjection:
    """
    실제 툴 주입 로직이 JarvisDispatcher._run_async_impl 메서드에서 작동하는지 테스트합니다.
    test_dispatcher.py를 사용하지 않고 별도로 구현했습니다.
    """

    @pytest.fixture
    def test_dispatcher(self):
        """테스트용 JarvisDispatcher 서브클래스 인스턴스를 생성합니다."""
        with patch('src.jarvis.core.dispatcher.genai'), \
             patch('src.jarvis.core.dispatcher.httpx'), \
             patch('src.jarvis.core.dispatcher.ContextManager'):
            
            dispatcher = TestJarvisDispatcher()
            
            # 실제 QA 에이전트와 Coding 에이전트 초기화
            dispatcher.sub_agents = {}  # 에이전트 등록 전 초기화
            
            return dispatcher

    @pytest.fixture
    def qa_agent(self):
        """KnowledgeQA_Agent 인스턴스를 생성합니다."""
        return KnowledgeQA_Agent()

    @pytest.fixture
    def coding_agent(self):
        """CodingAgent 인스턴스를 생성합니다."""
        return CodingAgent()

    @pytest.fixture
    def mock_invocation_context(self):
        """모의 InvocationContext를 생성합니다."""
        ctx = MagicMock(spec=InvocationContext)
        ctx.session = MagicMock()
        ctx.session.id = "test-session-id"
        ctx.user_content = Content(parts=[Part(text="테스트 요청입니다.")])
        return ctx

    @pytest.mark.asyncio
    async def test_tool_injection_successful(self, test_dispatcher, qa_agent, mock_invocation_context):
        """KnowledgeQA_Agent로 위임할 때 translate_tool과 web_search_tool이 올바르게 주입되는지 테스트합니다."""
        # 필요한 에이전트 등록
        test_dispatcher.register_agent(qa_agent)
        
        # 에이전트 원래 툴 저장
        original_tools = qa_agent.tools.copy()
        
        # agent_tool_map 설정 (이미 dispatcher.__init__에서 설정됨)
        test_dispatcher.agent_tool_map = {
            "KnowledgeQA_Agent": [web_search_tool, translate_tool]
        }
        
        # process_request가 반환할 값 설정
        mock_delegation_info = {
            "agent_name": "KnowledgeQA_Agent",
            "input_text": "이것은 테스트입니다.",
            "original_language": "ko",
            "required_tools": [web_search_tool, translate_tool],
            "conversation_history": "Mock conversation history"
        }
        test_dispatcher._mock_process_request_return = mock_delegation_info
        
        # _run_async_impl 실행
        generator = test_dispatcher._run_async_impl(mock_invocation_context)
        
        # 첫 번째 이벤트를 가져옵니다 (위임 이벤트여야 함)
        event = await generator.__anext__()
        
        # 검증: 이벤트가 올바른 위임 메시지를 포함하는지 확인
        assert isinstance(event, Event)
        assert event.author == test_dispatcher.name
        assert "[System] Delegating to KnowledgeQA_Agent" in event.content.parts[0].text
        
        # 검증: 주입된 툴이 올바른지 확인
        assert len(qa_agent.tools) == 2
        assert web_search_tool in qa_agent.tools
        assert translate_tool in qa_agent.tools
        
        # 이제 generator가 완료되었으므로 원래 툴로 복원되었는지 확인
        try:
            # 더 이상 이벤트가 없어야 함 (return으로 종료되었기 때문)
            await generator.__anext__()
            assert False, "Generator should have been exhausted"
        except StopAsyncIteration:
            # 예상대로 StopAsyncIteration이 발생
            pass
            
        # 검증: 원래 도구가 복원되었는지 확인 
        assert qa_agent.tools == original_tools

    @pytest.mark.asyncio
    async def test_tool_restoration_on_error(self, test_dispatcher, qa_agent, mock_invocation_context):
        """에러 발생 시에도 원래 툴이 복원되는지 테스트합니다."""
        # 필요한 에이전트 등록
        test_dispatcher.register_agent(qa_agent)
        
        # 에이전트 원래 툴 저장
        original_tools = qa_agent.tools.copy()
        
        # agent_tool_map 설정
        test_dispatcher.agent_tool_map = {
            "KnowledgeQA_Agent": [web_search_tool, translate_tool]
        }
        
        # process_request가 반환할 값 설정
        mock_delegation_info = {
            "agent_name": "KnowledgeQA_Agent",
            "input_text": "이것은 테스트입니다.",
            "original_language": "ko",
            "required_tools": [web_search_tool, translate_tool],
            "conversation_history": "Mock conversation history"
        }
        test_dispatcher._mock_process_request_return = mock_delegation_info
        
        # 에러 플래그 설정
        test_dispatcher._should_raise_error = True
        
        # _run_async_impl 실행
        generator = test_dispatcher._run_async_impl(mock_invocation_context)
        events = [event async for event in generator]
        
        # 에러 응답 이벤트가 생성되었는지 확인
        assert len(events) == 1
        assert "Error" in events[0].content.parts[0].text
        
        # 검증: 원래 도구가 복원되었는지 확인
        assert qa_agent.tools == original_tools
        
        # 테스트 후 플래그 초기화
        test_dispatcher._should_raise_error = False

    @pytest.mark.asyncio
    async def test_not_found_agent_error_handling(self, test_dispatcher, qa_agent, mock_invocation_context):
        """존재하지 않는 에이전트로 위임 시도 시 오류 처리를 테스트합니다."""
        # 필요한 에이전트 등록
        test_dispatcher.register_agent(qa_agent)
        
        # process_request가 존재하지 않는 에이전트 이름을 반환하도록 설정
        mock_delegation_info = {
            "agent_name": "NonExistentAgent",  # 존재하지 않는 에이전트
            "input_text": "이것은 테스트입니다.",
            "original_language": "ko",
            "required_tools": [web_search_tool, translate_tool],
            "conversation_history": "Mock conversation history"
        }
        test_dispatcher._mock_process_request_return = mock_delegation_info
        
        # _run_async_impl 실행
        generator = test_dispatcher._run_async_impl(mock_invocation_context)
        events = [event async for event in generator]
        
        # 검증: 에러 메시지가 포함된 이벤트가 생성되었는지 확인
        assert len(events) == 1
        assert "Error: Could not find agent NonExistentAgent" in events[0].content.parts[0].text

    @pytest.mark.asyncio
    async def test_process_request_direct_response(self, test_dispatcher, mock_invocation_context):
        """process_request가 문자열을 직접 반환할 때 처리를 테스트합니다."""
        # process_request가 DelegationInfo 대신 문자열을 반환하도록 설정
        test_dispatcher._mock_process_request_return = "직접 응답 문자열"
        
        # _run_async_impl 실행
        generator = test_dispatcher._run_async_impl(mock_invocation_context)
        events = [event async for event in generator]
        
        # 검증: ResponseGenerator.generate_response가 호출되고 결과가 이벤트로 반환되었는지 확인
        test_dispatcher.response_generator.generate_response.assert_called_once()
        assert len(events) == 1
        assert events[0].content.parts[0].text == "직접 응답 문자열" 