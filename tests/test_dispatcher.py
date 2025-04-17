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
    assert dispatcher.model == "gemini-2.0-flash-exp", f"예상 모델: gemini-2.0-flash-exp, 실제 모델: {dispatcher.model}"
    # assert isinstance(dispatcher.llm_config, LlmConfig), "llm_config는 LlmConfig의 인스턴스여야 합니다."
    # assert dispatcher.llm_config.model == "gemini-2.0-flash-exp", f"예상 모델: gemini-2.0-flash-exp, 실제 모델: {dispatcher.llm_config.model}"

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

# --- Fixtures for register_agent tests ---

@pytest.fixture
def dispatcher_instance():
    """테스트를 위한 JarvisDispatcher 인스턴스를 생성합니다."""
    return JarvisDispatcher()

@pytest.fixture
def mock_agent(mocker):
    """유효한 이름과 모델을 가진 Mock LlmAgent 객체를 생성합니다."""
    agent = mocker.Mock(spec=LlmAgent)
    agent.name = "MockAgent"
    agent.model = "mock-model"
    # 필요한 다른 속성이나 메서드도 모킹 가능
    # agent.description = "A mock agent for testing."
    return agent

@pytest.fixture
def mock_agent_no_name(mocker):
    """이름이 없는 Mock LlmAgent 객체를 생성합니다."""
    agent = mocker.Mock(spec=LlmAgent)
    agent.name = None # 이름 없음
    agent.model = "mock-model"
    return agent

# --- Tests for register_agent --- 

def test_register_agent_success(dispatcher_instance, mock_agent):
    """유효한 LlmAgent를 성공적으로 등록하는지 테스트합니다."""
    # Arrange
    initial_agent_count = len(dispatcher_instance.sub_agents)

    # Act
    dispatcher_instance.register_agent(mock_agent)

    # Assert
    assert len(dispatcher_instance.sub_agents) == initial_agent_count + 1
    assert mock_agent.name in dispatcher_instance.sub_agents
    assert dispatcher_instance.sub_agents[mock_agent.name] is mock_agent

def test_register_agent_success_message(dispatcher_instance, mock_agent, capsys):
    """에이전트 등록 성공 시 콘솔 메시지를 확인합니다."""
    # Act
    dispatcher_instance.register_agent(mock_agent)
    captured = capsys.readouterr()

    # Assert
    assert f"Agent '{mock_agent.name}' registered successfully." in captured.out

def test_register_agent_invalid_type(dispatcher_instance):
    """LlmAgent가 아닌 타입을 등록 시 TypeError를 발생하는지 테스트합니다."""
    # Arrange
    invalid_agent = object() # LlmAgent가 아님

    # Act & Assert
    with pytest.raises(TypeError, match="Registered agent must be an instance of LlmAgent"):
        dispatcher_instance.register_agent(invalid_agent)

def test_register_agent_no_name(dispatcher_instance, mock_agent_no_name):
    """이름이 없는 에이전트 등록 시 ValueError를 발생하는지 테스트합니다."""
    # Act & Assert
    with pytest.raises(ValueError, match="Registered agent must have a valid name."):
        dispatcher_instance.register_agent(mock_agent_no_name)

def test_register_agent_overwrite(dispatcher_instance, mock_agent, mocker):
    """동일한 이름의 에이전트를 다시 등록 시 덮어쓰는지 테스트합니다."""
    # Arrange: 먼저 에이전트 등록
    dispatcher_instance.register_agent(mock_agent)
    initial_instance = dispatcher_instance.sub_agents[mock_agent.name]

    # 새로운 Mock 에이전트 (같은 이름)
    new_mock_agent = mocker.Mock(spec=LlmAgent)
    new_mock_agent.name = mock_agent.name # 같은 이름
    new_mock_agent.model = "new-mock-model"

    # Act
    dispatcher_instance.register_agent(new_mock_agent)

    # Assert
    assert len(dispatcher_instance.sub_agents) == 1 # 개수는 동일
    assert dispatcher_instance.sub_agents[mock_agent.name] is new_mock_agent # 새 인스턴스로 덮어쓰여짐
    assert dispatcher_instance.sub_agents[mock_agent.name] is not initial_instance

def test_register_agent_overwrite_warning(dispatcher_instance, mock_agent, mocker, capsys):
    """에이전트 덮어쓰기 시 경고 메시지를 확인합니다."""
    # Arrange: 먼저 에이전트 등록
    dispatcher_instance.register_agent(mock_agent)
    _ = capsys.readouterr() # 이전 출력 비우기

    # 새로운 Mock 에이전트 (같은 이름)
    new_mock_agent = mocker.Mock(spec=LlmAgent)
    new_mock_agent.name = mock_agent.name
    new_mock_agent.model = "new-mock-model"

    # Act
    dispatcher_instance.register_agent(new_mock_agent)
    captured = capsys.readouterr()

    # Assert
    assert f"Warning: Agent with name '{mock_agent.name}' already registered. Overwriting." in captured.out
    assert f"Agent '{new_mock_agent.name}' registered successfully." in captured.out # 성공 메시지도 출력

# TODO: 추후 register_agent, process_request 등 다른 메서드에 대한 테스트 추가 