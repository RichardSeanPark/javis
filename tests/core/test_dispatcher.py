import pytest
import inspect # inspect 모듈 임포트
import asyncio # 비동기 테스트를 위해 추가
from unittest.mock import AsyncMock, MagicMock # AsyncMock, MagicMock 임포트

from src.jarvis.core.dispatcher import JarvisDispatcher
from src.jarvis.components.input_parser import InputParserAgent # 필요한 경우 임포트
from src.jarvis.models.input import ParsedInput # ParsedInput 임포트

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
 