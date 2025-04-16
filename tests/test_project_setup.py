import os
import pytest
import subprocess
import toml

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

def test_base_directories_creation():
    """
    테스트 목적: 기본 디렉토리가 올바르게 생성되었는지 확인합니다.
    테스트 방법: 각 디렉토리의 존재 여부를 확인합니다.
    """
    # 필수 디렉토리 목록
    required_directories = [
        'src',
        'tests',
        'docs', 
        'scripts',
        'data',
        'diagrams',
        'markdown',
        'config'
    ]
    
    # 각 디렉토리가 존재하는지 확인
    for directory in required_directories:
        assert os.path.exists(directory), f"{directory} 디렉토리가 존재하지 않습니다."
        assert os.path.isdir(directory), f"{directory}가 디렉토리가 아닙니다."

def test_dependencies_installation():
    """
    테스트 목적: 필요한 패키지들이 올바르게 설치되었는지 확인합니다.
    테스트 방법: pyproject.toml 파일에서 의존성 목록을 확인하고, 설치된 패키지 목록을 확인합니다.
    """
    # 필수 패키지 목록
    required_packages = [
        'google-adk',
        'google-cloud-aiplatform',
        'python-dotenv',
        'fastapi',
        'uvicorn',
        'pydantic'
    ]
    
    # poetry show 명령으로 설치된 패키지 목록 가져오기
    try:
        result = subprocess.run('poetry show', shell=True, check=True, text=True, capture_output=True)
        installed_packages = result.stdout
        
        # 각 패키지가 설치되어 있는지 확인
        for package in required_packages:
            assert package in installed_packages, f"{package} 패키지가 설치되지 않았습니다."
            
    except subprocess.CalledProcessError as e:
        pytest.fail(f"poetry show 명령 실행 실패: {e}")
        
    # pyproject.toml에서도 의존성 확인
    try:
        pyproject_content = toml.load('pyproject.toml')
        dependencies = []
        
        # 패키지명만 추출 (버전 정보 제외)
        if 'dependencies' in pyproject_content.get('project', {}):
            for dep in pyproject_content['project']['dependencies']:
                # 패키지명만 추출 (버전 정보 제외)
                if ' ' in dep:
                    dep_name = dep.split(' ')[0].lower()
                else:
                    dep_name = dep.lower()
                dependencies.append(dep_name)
                
        # 필수 패키지가 의존성 목록에 있는지 확인 (대소문자 구분 없이)
        for package in required_packages:
            # uvicorn[standard]의 경우 uvicorn으로 확인
            if package.startswith('uvicorn'):
                package = 'uvicorn'
            assert package.lower() in dependencies or any(package.lower() in dep.lower() for dep in dependencies), \
                f"{package} 패키지가 pyproject.toml의 의존성 목록에 없습니다."
                
    except Exception as e:
        pytest.fail(f"pyproject.toml 파일 읽기 또는 의존성 확인 실패: {e}")

def test_gitignore_creation():
    """
    테스트 목적: .gitignore 파일이 올바르게 생성되었는지 확인합니다.
    테스트 방법: 파일 존재 여부와 필수 패턴 포함 여부를 확인합니다.
    """
    # .gitignore 파일 존재 확인
    assert os.path.exists('.gitignore'), ".gitignore 파일이 존재하지 않습니다."
    
    # .gitignore 파일 내용 읽기
    with open('.gitignore', 'r') as f:
        gitignore_content = f.read()
    
    # 필수 패턴 목록
    required_patterns = [
        '__pycache__/',
        '*.py[cod]',
        '.env',
        '.idea/',
        '.vscode/',
        '.DS_Store'
    ]
    
    # 각 패턴이 .gitignore 파일에 포함되어 있는지 확인
    for pattern in required_patterns:
        assert pattern in gitignore_content, f"{pattern} 패턴이 .gitignore 파일에 포함되어 있지 않습니다."

def test_readme_creation():
    """
    테스트 목적: README.md 파일이 올바르게 생성되었는지 확인합니다.
    테스트 방법: 파일 존재 여부와 필수 내용 포함 여부를 확인합니다.
    """
    # README.md 파일 존재 확인
    assert os.path.exists('README.md'), "README.md 파일이 존재하지 않습니다."
    
    # README.md 파일 내용 읽기
    with open('README.md', 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # 필수 내용 목록
    required_contents = [
        'Jarvis AI Framework',
        '설치',
        '시작하기',
        '라이선스'
    ]
    
    # 각 내용이 README.md 파일에 포함되어 있는지 확인
    for content in required_contents:
        assert content in readme_content, f"{content} 내용이 README.md 파일에 포함되어 있지 않습니다." 