import pytest
import inspect # inspect 모듈 임포트
from src.jarvis.core.dispatcher import JarvisDispatcher
from src.jarvis.components.input_parser import InputParserAgent # 필요한 경우 임포트

# Fixture for JarvisDispatcher instance (if needed later)
@pytest.fixture
def dispatcher():
    return JarvisDispatcher()

# Test class for JarvisDispatcher
class TestJarvisDispatcher:

    def test_process_request_is_async(self, dispatcher):
        """process_request 메서드가 async def로 정의되었는지 확인합니다."""
        assert inspect.iscoroutinefunction(dispatcher.process_request), \
            "process_request 메서드는 async def여야 합니다."

    def test_process_request_accepts_string_input(self, dispatcher):
        """process_request 메서드가 'user_input' 문자열 인자를 받는지 확인합니다."""
        sig = inspect.signature(dispatcher.process_request)
        params = sig.parameters
        assert 'user_input' in params, "process_request 메서드는 'user_input' 인자를 가져야 합니다."
        assert params['user_input'].annotation == str, \
            "'user_input' 인자의 타입 힌트는 str이어야 합니다."
        # 간단히 호출 가능한지 확인 (실제 로직은 아직 없으므로 None 반환 예상)
        # pytest.mark.asyncio 데코레이터가 필요할 수 있음
        # async def test_wrapper():
        #     await dispatcher.process_request("test input")
 