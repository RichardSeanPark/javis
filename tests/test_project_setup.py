import os
import pytest
import subprocess

def test_github_repository_creation():
    """
    테스트 목적: Github repository가 올바르게 생성되었는지 확인합니다.
    테스트 방법: 로컬 Git 저장소 초기화 및 원격 저장소 설정 확인
    """
    # 로컬 git 저장소 확인
    assert os.path.exists('.git'), ".git 디렉토리가 존재하지 않습니다. git init이 실행되지 않았습니다."
    
    # 원격 저장소 설정 확인
    try:
        result = subprocess.run('git remote -v', shell=True, check=True, text=True, capture_output=True)
        remote_output = result.stdout
        
        # 원격 저장소 URL에 username과 repo_name이 포함되어 있는지 확인
        expected_remote = "github.com/RichardSeanPark/javis"
        assert expected_remote in remote_output, f"원격 저장소가 올바르게 설정되지 않았습니다."
        
    except subprocess.CalledProcessError as e:
        pytest.fail(f"git remote 명령 실행 실패: {e}") 