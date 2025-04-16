"""
커스텀 웹 UI (FastAPI) 테스트
"""

import os
import pytest
import subprocess
import importlib.util
import sys
import requests
from pathlib import Path
import time


def test_api_main_file_exists():
    """
    테스트 목적: src/jarvis/interfaces/api/main.py 파일이 존재하는지 확인합니다.
    테스트 방법: 파일의 존재 여부를 확인합니다.
    """
    main_path = Path('src/jarvis/interfaces/api/main.py')
    assert main_path.exists(), "src/jarvis/interfaces/api/main.py 파일이 존재하지 않습니다."
    
    init_path = Path('src/jarvis/interfaces/api/__init__.py')
    assert init_path.exists(), "src/jarvis/interfaces/api/__init__.py 파일이 존재하지 않습니다."


def test_fastapi_app_creation():
    """
    테스트 목적: FastAPI 앱 인스턴스가 생성되었는지 확인합니다.
    테스트 방법: 모듈을 로드하여 app 변수가 FastAPI 인스턴스인지 확인합니다.
    """
    # 현재 작업 디렉토리를 sys.path에 추가하여 src 모듈을 불러올 수 있게 합니다
    sys.path.insert(0, os.getcwd())
    
    try:
        # 모듈 임포트 시도
        spec = importlib.util.spec_from_file_location(
            "main", "src/jarvis/interfaces/api/main.py"
        )
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        # FastAPI 앱 인스턴스 확인
        from fastapi import FastAPI
        assert hasattr(main_module, 'app'), "app 변수가 정의되어 있지 않습니다."
        assert isinstance(main_module.app, FastAPI), "app 변수가 FastAPI 인스턴스가 아닙니다."
        
    except ImportError as e:
        pytest.fail(f"모듈 임포트 실패: {e}")
    finally:
        # sys.path에서 현재 작업 디렉토리 제거
        if os.getcwd() in sys.path:
            sys.path.remove(os.getcwd())


def test_root_endpoint_definition():
    """
    테스트 목적: 루트 경로('/')에 대한 GET 요청 핸들러 함수가 정의되어 있는지 확인합니다.
    테스트 방법: 모듈을 로드하여 read_root 함수가 정의되어 있는지 확인합니다.
    """
    # 현재 작업 디렉토리를 sys.path에 추가하여 src 모듈을 불러올 수 있게 합니다
    sys.path.insert(0, os.getcwd())
    
    try:
        # 모듈 임포트 시도
        spec = importlib.util.spec_from_file_location(
            "main", "src/jarvis/interfaces/api/main.py"
        )
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        
        # read_root 함수 확인
        assert hasattr(main_module, 'read_root'), "read_root 함수가 정의되어 있지 않습니다."
        
    except ImportError as e:
        pytest.fail(f"모듈 임포트 실패: {e}")
    finally:
        # sys.path에서 현재 작업 디렉토리 제거
        if os.getcwd() in sys.path:
            sys.path.remove(os.getcwd())


def test_execution_script():
    """
    테스트 목적: 실행 스크립트가 추가되었는지 확인합니다.
    테스트 방법: pyproject.toml 파일과 별도의 run_api.py 파일을 확인합니다.
    """
    # pyproject.toml 파일 확인
    import toml
    
    try:
        with open('pyproject.toml', 'r') as f:
            pyproject = toml.load(f)
        
        # project.scripts 섹션 확인
        has_script = 'scripts' in pyproject.get('project', {}) and 'run-api' in pyproject['project']['scripts']
        
        # 별도의 run_api.py 파일 확인
        has_script_file = Path('run_api.py').exists()
        
        assert has_script or has_script_file, "실행 스크립트가 추가되지 않았습니다."
        
    except Exception as e:
        pytest.fail(f"실행 스크립트 확인 실패: {e}")


@pytest.mark.skip(reason="이 테스트는 실제 서버를 시작하므로 별도로 실행해야 합니다.")
def test_api_server_startup():
    """
    테스트 목적: uvicorn으로 API 서버가 정상적으로 시작되는지 확인합니다.
    테스트 방법: 서버를 실행하고 응답 확인 후 종료합니다.
    
    참고: 이 테스트는 실제 서버를 시작하므로 CI 환경 등에서는 별도 처리 필요
    """
    # 이 테스트는 실제 서버를 시작하므로 skip 처리하거나 mock으로 대체 가능
    pass


def test_api_welcome_message():
    """
    테스트 목적: API 서버의 루트 경로에서 정상적인 응답이 오는지 확인합니다.
    테스트 방법: HTTP 요청을 보내고 응답을 확인합니다.
    
    참고: 이 테스트는 실행 중인 서버가 필요하므로 CI 환경 등에서는 별도 처리 필요
    """
    try:
        response = requests.get('http://localhost:8088/')
        assert response.status_code == 200, f"API 서버 응답이 200이 아닙니다. 응답: {response.status_code}"
        assert response.json().get('message') == "Welcome to Jarvis API", \
            f"API 서버 응답 내용이 예상과 다릅니다. 응답: {response.json()}"
    except requests.exceptions.ConnectionError:
        pytest.fail("API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        pytest.fail(f"API 서버 응답 확인 실패: {e}") 