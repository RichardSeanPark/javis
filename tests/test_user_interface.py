import os
import pytest
import sys
import subprocess
import importlib
from pathlib import Path

def test_init_file_imports():
    """
    테스트 목적: src/jarvis/__init__.py 파일이 root_agent를 올바르게 임포트하는지 확인합니다.
    테스트 방법: 파일의 존재 여부와 내용을 확인합니다.
    """
    # src/jarvis/__init__.py 파일 존재 확인
    init_path = Path('src/jarvis/__init__.py')
    assert init_path.exists(), "src/jarvis/__init__.py 파일이 존재하지 않습니다."
    
    # 파일 내용 읽기
    with open(init_path, 'r', encoding='utf-8') as f:
        init_content = f.read()
    
    # root_agent 임포트 확인
    assert "from .core.dispatcher import root_agent" in init_content or "from .core.dispatcher import root_agent as agent" in init_content, \
        "src/jarvis/__init__.py 파일에 root_agent 임포트가 없습니다."

def test_dispatcher_file_exists():
    """
    테스트 목적: src/jarvis/core/dispatcher.py 파일이 존재하는지 확인합니다.
    테스트 방법: 파일의 존재 여부를 확인합니다.
    """
    dispatcher_path = Path('src/jarvis/core/dispatcher.py')
    assert dispatcher_path.exists(), "src/jarvis/core/dispatcher.py 파일이 존재하지 않습니다."

def test_root_agent_definition():
    """
    테스트 목적: root_agent가 올바르게 정의되어 있는지 확인합니다.
    테스트 방법: 모듈을 로드하여 root_agent의 타입과 속성을 확인합니다.
    """
    # 현재 작업 디렉토리를 sys.path에 추가하여 src 모듈을 불러올 수 있게 합니다
    sys.path.insert(0, os.getcwd())
    
    try:
        # 모듈 임포트 시도
        from src.jarvis.core.dispatcher import root_agent
        from google.adk import Agent
        
        # root_agent가 Agent 클래스의 인스턴스인지 확인
        assert isinstance(root_agent, Agent), "root_agent가 Agent 클래스의 인스턴스가 아닙니다."
        
        # root_agent의 name과 description 확인
        assert root_agent.name == "JarvisDispatcherPlaceholder", f"root_agent의 name이 'JarvisDispatcherPlaceholder'가 아닙니다. 현재 값: {root_agent.name}"
        assert root_agent.description == "Jarvis AI Framework Root Agent (Placeholder)", \
            f"root_agent의 description이 올바르지 않습니다. 현재 값: {root_agent.description}"
    
    except ImportError as e:
        pytest.fail(f"모듈 임포트 실패: {e}")
    finally:
        # sys.path에서 현재 작업 디렉토리 제거
        if os.getcwd() in sys.path:
            sys.path.remove(os.getcwd())

def test_cli_execution():
    """
    테스트 목적: CLI 인터페이스가 정상적으로 실행되는지 확인합니다.
    테스트 방법: 'adk run .' 명령어를 실행하고 출력을 확인합니다.
    
    참고: 이 테스트는 실제로 실행하면 대화형 프롬프트를 시작하므로, 
    실제 환경에서는 비활성화하거나 다른 방법으로 테스트해야 할 수 있습니다.
    """
    # 이 테스트는 mock으로 대체하거나 실제 환경에서는 skip할 수 있음
    # pytest.skip("대화형 프롬프트를 시작하는 테스트이므로 실제 실행 시 스킵됩니다.")
    
    # 아래는 실제 실행 대신 설치 여부만 확인하는 방식으로 대체
    try:
        result = subprocess.run('which adk', shell=True, check=True, text=True, capture_output=True)
        adk_path = result.stdout.strip()
        assert adk_path, "adk 명령어를 찾을 수 없습니다. Google ADK가 설치되어 있지 않거나 PATH에 없습니다."
    except subprocess.CalledProcessError:
        pytest.fail("adk 명령어를 확인하는 데 실패했습니다.")

def test_web_ui_prerequisites():
    """
    테스트 목적: 웹 UI 실행을 위한 전제 조건이 만족되는지 확인합니다.
    테스트 방법: 1.1 단계의 구현 완료 여부를 확인합니다.
    """
    # 1.1 단계의 테스트들이 통과했는지 확인 (여기서는 이전 테스트에 의존)
    test_init_file_imports()
    test_dispatcher_file_exists()
    test_root_agent_definition()
    test_cli_execution()

def test_web_ui_execution():
    """
    테스트 목적: 웹 UI가 정상적으로 실행되는지 확인합니다.
    테스트 방법: 'adk web .' 명령어 실행 가능 여부를 확인합니다.
    
    참고: 이 테스트는 실제로 실행하면 웹 서버를 시작하므로,
    실제 환경에서는 비활성화하거나 다른 방법으로 테스트해야 할 수 있습니다.
    """
    # 이 테스트는 mock으로 대체하거나 실제 환경에서는 skip할 수 있음
    # pytest.skip("웹 서버를 시작하는 테스트이므로 실제 실행 시 스킵됩니다.")
    
    # 아래는 실제 실행 대신 설치 여부만 확인하는 방식으로 대체
    try:
        result = subprocess.run('which adk', shell=True, check=True, text=True, capture_output=True)
        adk_path = result.stdout.strip()
        assert adk_path, "adk 명령어를 찾을 수 없습니다. Google ADK가 설치되어 있지 않거나 PATH에 없습니다."
    except subprocess.CalledProcessError:
        pytest.fail("adk 명령어를 확인하는 데 실패했습니다.") 