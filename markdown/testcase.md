# 자비스 AI 프레임워크 테스트 케이스

## 0. 프로젝트 초기 설정 테스트

### 0.1. Poetry 초기화 테스트
- [X] pyproject.toml 파일 존재 확인
- [X] project 섹션 확인 (name, version, description 등)
- [X] build-system 섹션 확인
- [X] 의존성 목록 확인

### 0.2. Git Repository 생성 테스트
- [X] .git 디렉토리 존재 확인
- [X] 원격 저장소 설정 확인 (github.com/RichardSeanPark/javis)

### 0.3. 기본 디렉토리 생성 테스트
- [X] src 디렉토리 존재 확인
- [X] tests 디렉토리 존재 확인
- [X] docs 디렉토리 존재 확인
- [X] scripts 디렉토리 존재 확인
- [X] data 디렉토리 존재 확인
- [X] diagrams 디렉토리 존재 확인
- [X] markdown 디렉토리 존재 확인
- [X] config 디렉토리 존재 확인

### 0.4. 초기 의존성 추가 테스트
- [X] google-adk 패키지 설치 확인
- [X] google-cloud-aiplatform 패키지 설치 확인
- [X] python-dotenv 패키지 설치 확인
- [X] fastapi 패키지 설치 확인
- [X] uvicorn 패키지 설치 확인
- [X] pydantic 패키지 설치 확인

### 0.5. .gitignore 파일 생성 테스트
- [X] .gitignore 파일 존재 확인
- [X] 필수 패턴 포함 확인 (__pycache__, *.py[cod], .env)
- [X] IDE 설정 파일 패턴 확인 (.idea/, .vscode/)
- [X] OS 특정 파일 패턴 확인 (.DS_Store)

### 0.6. README.md 파일 생성 테스트
- [X] README.md 파일 존재 확인
- [X] 프로젝트 제목 포함 확인
- [X] 프로젝트 설명 포함 확인
- [X] 설치 및 사용 방법 포함 확인

### 0.7. .env.example 파일 생성 테스트
- [X] .env.example 파일 존재 확인
- [X] 필수 환경 변수 포함 확인 (GEMINI_API_KEY, GCP_PROJECT_ID)
- [X] 환경 변수 값이 비어있는지 확인

### 0.8. 기본 src 구조 생성 테스트
- [X] src/jarvis 디렉토리 존재 확인
- [X] src/jarvis/__init__.py 파일 존재 확인
- [X] core, components, agents, tools, interfaces, models 하위 디렉토리 존재 확인
- [X] 각 하위 디렉토리에 __init__.py 파일 존재 확인

## 1. 사용자 인터페이스 계층 테스트

### 1.1. CLI 인터페이스 (ADK 활용) 테스트
- [X] src/jarvis/__init__.py 파일에 root_agent 임포트 확인
- [X] src/jarvis/core/dispatcher.py 파일 존재 확인
- [X] root_agent 변수가 Agent 클래스의 인스턴스인지 확인
- [X] root_agent의 name이 "JarvisDispatcherPlaceholder"인지 확인
- [X] root_agent의 description이 "Jarvis AI Framework Root Agent (Placeholder)"인지 확인
- [X] "adk run ." 명령어 실행 시 JarvisDispatcherPlaceholder 에이전트가 로드되는지 확인

### 1.2. 웹 UI (ADK Web 활용) 테스트
- [X] (선행 작업) 1.1의 임시 에이전트 정의 완료 확인
- [X] "adk web ." 명령어 실행 시 웹 서버가 정상적으로 시작되는지 확인
- [X] 웹 브라우저에서 http://localhost:8000 접속 시 ADK Web UI가 로드되는지 확인
- [X] JarvisDispatcherPlaceholder 에이전트가 UI에서 선택 가능한지 확인

### 1.3. 커스텀 웹 UI (FastAPI + React) 테스트
- [X] src/jarvis/interfaces/api/main.py 파일 존재 확인
- [X] FastAPI 앱 인스턴스가 생성되었는지 확인
- [X] 루트 경로('/')에 대한 GET 요청 핸들러 함수 정의 확인
- [X] 실행 스크립트가 추가되었는지 확인 (pyproject.toml 또는 별도 run_api.py)
- [X] uvicorn으로 API 서버 실행 시 정상 시작되는지 확인
- [X] "http://localhost:8088/"에 접속하여 "Welcome to Jarvis API" 메시지 확인

## 2. 입력 처리 및 파싱 계층 테스트

### 2.1. 데이터 모델 정의 테스트
- [X] src/jarvis/models/input.py 파일 존재 확인
- [X] ParsedInput 클래스가 pydantic.BaseModel을 상속하는지 확인
- [X] 필수 필드(original_text, original_language, english_text) 존재 확인
- [X] 선택적 필드(intent, entities, domain) 존재 확인
- [X] 각 필드의 타입 및 기본값 설정 확인

### 2.2. InputParserAgent 클래스 정의 테스트
- [X] src/jarvis/components/input_parser.py 파일 존재 확인
- [X] InputParserAgent 클래스가 LlmAgent를 상속하는지 확인
- [X] __init__ 메서드에서 적절한 이름과 설명, "gemini-pro" 모델 설정 확인
- [X] process_input 메서드 존재 확인 (비동기 함수)
- [X] src/jarvis/components/__init__.py에 InputParserAgent 모듈 등록 확인

### 2.3. 언어 감지 기능 테스트
- [X] _detect_language 메서드 존재 확인
- [-] 영어 텍스트 입력 시 'en' 반환 확인
- [-] 한국어 텍스트 입력 시 'ko' 반환 확인
- [-] 일본어 텍스트 입력 시 'ja' 반환 확인
- [-] 중국어 텍스트 입력 시 'zh' 반환 확인

### 2.4. 영어 번역 기능 테스트
- [X] _translate_to_english 메서드 존재 확인
- [-] 한국어 텍스트 입력 시 올바른 영어 번역 반환 확인
- [-] 원본이 영어인 경우 그대로 반환하는 로직 확인

### 2.5. 의도/엔티티/도메인 분석 기능 테스트
- [X] _analyze_intent_and_entities 메서드 존재 확인
- [-] "파이썬으로 피보나치 수열 코드 작성해줘" 입력 시 의도가 'code_generation'으로 분석되는지 확인
- [-] "파이썬으로 피보나치 수열 코드 작성해줘" 입력 시 도메인이 'coding'으로 분석되는지 확인
- [-] "내일 서울 날씨 어때?" 입력 시 적절한 엔티티 추출 확인

### 2.6. ParsedInput 객체 생성 및 반환 테스트
- [X] 한국어 입력 시 모든 필드가 올바르게 설정된 ParsedInput 객체 반환 확인
- [X] 영어 입력 시 모든 필드가 올바르게 설정된 ParsedInput 객체 반환 확인
- [X] JSON 직렬화/역직렬화 확인
