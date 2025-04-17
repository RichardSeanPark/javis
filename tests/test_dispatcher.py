import pytest
from google.adk.agents import LlmAgent
# LlmConfig는 더 이상 사용되지 않음
# from google.adk.models import LlmConfig 
from src.jarvis.core.dispatcher import JarvisDispatcher
from src.jarvis.components.input_parser import InputParserAgent

# pytest.mark.usefixtures("load_env") # .env 파일 로드 (필요시)

# @pytest.mark.usefixtures("init_dispatcher") # Fixture 사용 예시 (필요시)
# def test_jarvis_dispatcher_init_fixture(dispatcher):
#     """Fixture를 사용한 JarvisDispatcher 초기화 테스트"""
#     # ... 아래 테스트 내용과 동일 ...

def test_jarvis_dispatcher_init():
    """JarvisDispatcher 초기화 테스트"""
    # Arrange & Act: JarvisDispatcher 인스턴스 생성
    try:
        dispatcher = JarvisDispatcher()
    except Exception as e:
        pytest.fail(f"JarvisDispatcher 인스턴스 생성 중 오류 발생: {e}")

    # Assert: 속성 검증
    assert isinstance(dispatcher, LlmAgent), "JarvisDispatcher는 LlmAgent를 상속해야 합니다."
    assert dispatcher.name == "JarvisDispatcher", f"예상 이름: JarvisDispatcher, 실제 이름: {dispatcher.name}"
    assert dispatcher.description == "Central dispatcher for the Jarvis AI Framework. Analyzes requests and routes them to the appropriate specialized agent.", "Description이 예상과 다릅니다."

    # LlmAgent 인스턴스에 llm_config 속성이 직접 존재하지 않을 수 있음. 
    # 대신 model 속성을 확인하거나, 필요시 내부 구현 확인
    assert hasattr(dispatcher, 'model'), "LlmAgent 인스턴스에 model 속성이 있어야 합니다."
    assert dispatcher.model == "gemini-2.0-flash-exp", f"예상 모델: gemini-pro, 실제 모델: {dispatcher.model}"
    # assert isinstance(dispatcher.llm_config, LlmConfig), "llm_config는 LlmConfig의 인스턴스여야 합니다."
    # assert dispatcher.llm_config.model == "gemini-pro", f"예상 모델: gemini-pro, 실제 모델: {dispatcher.llm_config.model}"

    assert isinstance(dispatcher.input_parser, InputParserAgent), "input_parser는 InputParserAgent의 인스턴스여야 합니다."
    assert dispatcher.sub_agents == {}, f"sub_agents는 빈 딕셔너리여야 합니다. 실제 값: {dispatcher.sub_agents}"

# Fixture 정의 예시 (필요시)
# @pytest.fixture(scope="module")
# def load_env():
#     from dotenv import load_dotenv
#     load_dotenv()

# @pytest.fixture
# def init_dispatcher(load_env):
#     return JarvisDispatcher()

# TODO: 추후 register_agent, process_request 등 다른 메서드에 대한 테스트 추가 