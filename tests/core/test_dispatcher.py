import pytest
import inspect # inspect 모듈 임포트
import asyncio # 비동기 테스트를 위해 추가
from unittest.mock import AsyncMock, MagicMock, patch # patch 추가

from src.jarvis.core.dispatcher import JarvisDispatcher
from src.jarvis.components.input_parser import InputParserAgent # 필요한 경우 임포트
from src.jarvis.models.input import ParsedInput # ParsedInput 임포트
from google.adk.agents import LlmAgent # LlmAgent 임포트 추가

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

# Mock Agent 클래스 정의
class MockAgent(LlmAgent):
    def __init__(self, name="MockAgent", description="A mock agent.", model="mock-model"):
        super().__init__(name=name, description=description, model=model)

# Test class for JarvisDispatcher
@pytest.mark.asyncio # 클래스 전체에 비동기 테스트 적용
class TestJarvisDispatcher:

    async def test_process_request_is_async(self, dispatcher):
        """process_request 메서드가 async def로 정의되었는지 확인합니다."""
        assert inspect.iscoroutinefunction(dispatcher.process_request), \
            "process_request 메서드는 async def여야 합니다."

    async def test_process_request_accepts_string_input(self, dispatcher):
        """process_request 메서드가 'user_input' 문자열 인자를 받는지 확인합니다."""
        sig = inspect.signature(dispatcher.process_request)
        params = sig.parameters
        assert 'user_input' in params, "process_request 메서드는 'user_input' 인자를 가져야 합니다."
        assert params['user_input'].annotation == str, \
            "'user_input' 인자의 타입 힌트는 str이어야 합니다."

    async def test_process_request_calls_input_parser(self, mocker):
        """process_request가 self.input_parser.process_input을 호출하고 결과를 저장하는지 확인합니다."""
        # Arrange
        mock_parsed_input = MagicMock(spec=ParsedInput) # 모의 반환값
        mock_parsed_input.original_language = 'ko' # 모의 언어 코드 설정
        mock_parsed_input.intent = None # intent 속성 추가 (오류 방지)
        mock_parsed_input.domain = None # domain 속성 추가 (오류 방지)
        # InputParserAgent.process_input을 AsyncMock으로 모킹
        mock_process_input = AsyncMock(return_value=mock_parsed_input)
        # mocker.patch.object를 사용하면 클래스의 메서드를 직접 패치할 수 있습니다.
        # InputParserAgent 인스턴스가 생성될 때 process_input이 이 mock을 사용하게 됩니다.
        mocker.patch.object(InputParserAgent, 'process_input', new=mock_process_input)
        
        # Dispatcher 인스턴스 생성 
        dispatcher_instance = JarvisDispatcher()
        test_input = "테스트 입력"

        # Act
        await dispatcher_instance.process_request(test_input)

        # Assert
        # process_input이 test_input 인자와 함께 한 번 호출되었는지 확인
        mock_process_input.assert_awaited_once_with(test_input)
        # 결과가 인스턴스 변수에 저장되었는지 확인
        assert dispatcher_instance.current_parsed_input == mock_parsed_input
        assert dispatcher_instance.current_original_language == 'ko'

    # 이전 fixture 방식 사용 시:
    # async def test_process_request_calls_input_parser_with_fixture(self, dispatcher, mock_input_parser):
    #     """process_request가 self.input_parser.process_input을 호출하는지 확인합니다 (Fixture 사용)."""
    #     # Arrange
    #     test_input = "테스트 입력"
    #     mock_parsed_result = MagicMock(spec=ParsedInput) # 모의 결과
    #     mock_input_parser.process_input.return_value = mock_parsed_result

    #     # Act
    #     # dispatcher fixture가 mock_input_parser를 사용하도록 설정 필요
    #     # 여기서는 dispatcher 인스턴스가 이미 mock_input_parser를 내부적으로 갖는다고 가정
    #     result = await dispatcher.process_request(test_input)

    #     # Assert
    #     mock_input_parser.process_input.assert_awaited_once_with(test_input)
    #     # 결과 할당 확인은 직접적이지 않음

    # 참고: 현재 dispatcher fixture는 InputParserAgent를 모킹하지 않음.
    #       InputParserAgent를 직접 모킹하는 것이 더 명확할 수 있음.
    #       위의 test_process_request_calls_input_parser가 더 적합한 접근 방식일 수 있음.

    # Helper to setup mocks for routing tests
    def _setup_routing_mocks(self, mocker, intent, domain, sub_agents_config):
        mock_parsed_input = MagicMock(spec=ParsedInput)
        mock_parsed_input.intent = intent
        mock_parsed_input.domain = domain
        mock_parsed_input.original_language = 'en' # 예시

        mock_process_input = AsyncMock(return_value=mock_parsed_input)
        mocker.patch.object(InputParserAgent, 'process_input', new=mock_process_input)

        dispatcher_instance = JarvisDispatcher()
        
        # sub_agents 설정
        dispatcher_instance.sub_agents = {}
        for agent_name, agent_instance in sub_agents_config.items():
            dispatcher_instance.register_agent(agent_instance)
            
        return dispatcher_instance, mock_process_input # mock_process_input 반환 추가

    async def test_routing_to_coding_agent_by_intent(self, mocker):
        """intent='code_generation'일 때 CodingAgent로 라우팅되는지 확인"""
        coding_agent = MockAgent(name="CodingAgent")
        dispatcher, _ = self._setup_routing_mocks(mocker, 'code_generation', 'other', {"CodingAgent": coding_agent})
        
        # process_request 실행 (실제 selected_agent는 로컬 변수)
        # 테스트를 위해 라우팅 결과를 확인할 방법 필요 (예: print 캡처, 임시 반환값 수정 등)
        # 여기서는 개념적으로 확인 (실제 테스트 코드에서는 조정 필요)
        with patch('builtins.print') as mock_print: # print문 캡처
            await dispatcher.process_request("input")
            mock_print.assert_any_call("Routing to: CodingAgent")

    async def test_routing_to_coding_agent_by_domain(self, mocker):
        """domain='coding'일 때 CodingAgent로 라우팅되는지 확인"""
        coding_agent = MockAgent(name="CodingAgent")
        dispatcher, _ = self._setup_routing_mocks(mocker, 'other', 'coding', {"CodingAgent": coding_agent})
        with patch('builtins.print') as mock_print:
            await dispatcher.process_request("input")
            mock_print.assert_any_call("Routing to: CodingAgent")

    async def test_routing_to_qa_agent_by_intent(self, mocker):
        """intent='question_answering'일 때 KnowledgeQA_Agent로 라우팅되는지 확인"""
        qa_agent = MockAgent(name="KnowledgeQA_Agent")
        dispatcher, _ = self._setup_routing_mocks(mocker, 'question_answering', 'other', {"KnowledgeQA_Agent": qa_agent})
        with patch('builtins.print') as mock_print:
            await dispatcher.process_request("input")
            mock_print.assert_any_call("Routing to: KnowledgeQA_Agent")

    async def test_routing_to_qa_agent_by_domain(self, mocker):
        """domain='general'일 때 KnowledgeQA_Agent로 라우팅되는지 확인"""
        qa_agent = MockAgent(name="KnowledgeQA_Agent")
        dispatcher, _ = self._setup_routing_mocks(mocker, 'other', 'general', {"KnowledgeQA_Agent": qa_agent})
        with patch('builtins.print') as mock_print:
            await dispatcher.process_request("input")
            mock_print.assert_any_call("Routing to: KnowledgeQA_Agent")
            
    async def test_routing_no_match(self, mocker):
        """일치하는 intent/domain이 없을 때 라우팅되지 않는지 확인"""
        coding_agent = MockAgent(name="CodingAgent")
        qa_agent = MockAgent(name="KnowledgeQA_Agent")
        dispatcher, _ = self._setup_routing_mocks(mocker, 'unknown_intent', 'unknown_domain', {"CodingAgent": coding_agent, "KnowledgeQA_Agent": qa_agent})
        with patch('builtins.print') as mock_print:
            await dispatcher.process_request("input")
            mock_print.assert_any_call("No suitable agent found for routing.")

    async def test_routing_agent_not_registered(self, mocker):
        """intent/domain은 맞지만 해당 에이전트가 없을 때 라우팅되지 않는지 확인"""
        # CodingAgent만 등록된 상태에서 QA 요청
        coding_agent = MockAgent(name="CodingAgent")
        dispatcher, _ = self._setup_routing_mocks(mocker, 'question_answering', 'general', {"CodingAgent": coding_agent})
        with patch('builtins.print') as mock_print:
            await dispatcher.process_request("input")
            mock_print.assert_any_call("No suitable agent found for routing.")

    async def test_routing_no_parsed_input(self, mocker):
        """parsed_input이 None일 때 라우팅되지 않는지 확인"""
        # process_input이 None을 반환하도록 모킹
        mock_process_input = AsyncMock(return_value=None)
        mocker.patch.object(InputParserAgent, 'process_input', new=mock_process_input)
        dispatcher_instance = JarvisDispatcher()
        # sub_agents는 비어있어도 됨
        dispatcher_instance.sub_agents = {}

        with patch('builtins.print') as mock_print:
            await dispatcher_instance.process_request("input")
            # input_parser 호출은 확인
            mock_process_input.assert_awaited_once_with("input")
            # 라우팅 실패 확인
            mock_print.assert_any_call("No suitable agent found for routing.")
 