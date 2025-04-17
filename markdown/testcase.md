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

### 2.1. 데이터 모델 (ParsedInput) 테스트
- [X] `src/jarvis/models/input.py` 파일 존재 확인
- [X] `ParsedInput` 클래스가 `BaseModel`을 상속하는지 확인
- [X] 필수 필드(`original_text`, `original_language`, `english_text`)가 정의되어 있는지 확인
- [X] 선택적 필드(`intent`, `entities`, `domain`)가 정의되어 있는지 확인
- [X] 필수 필드 누락 시 유효성 검사 오류 발생하는지 확인
- [X] 모든 필드에 올바른 타입의 값을 할당할 수 있는지 확인
- [X] 선택적 필드에 `None` 값을 할당할 수 있는지 확인

### 2.2. InputParserAgent 클래스 정의 테스트
- [X] `src/jarvis/components/input_parser.py` 파일 존재 확인
- [X] `InputParserAgent` 클래스가 `LlmAgent`를 상속하는지 확인
- [X] `__init__` 메서드가 "InputParser" 이름, 설명, `model` ID로 부모 클래스를 초기화하는지 확인
- [X] `process_input` 메서드가 정의되어 있고, `user_input` 문자열을 인자로 받고 `ParsedInput` 객체를 반환하는지 확인 (타입 힌트 및 비동기 확인)
- [ ] **언어 감지 테스트**: 다양한 언어 입력에 대해 `self.llm.generate_content`가 올바른 프롬프트로 호출되는지 확인 (Mock 사용)
- [ ] **언어 감지 테스트**: LLM 응답(Mock)이 주어졌을 때, 언어 코드가 정확히 파싱되어 `ParsedInput.original_language`에 저장되는지 확인 (예: "ko", "en", "ja")
- [ ] **언어 감지 테스트**: LLM 응답(Mock)이 예상치 못한 형식일 때 기본값('en')이 사용되는지 확인
- [ ] **언어 감지 테스트**: LLM 호출 중 예외 발생 시 기본값('en')이 사용되고 오류가 로깅되는지 확인 (Mock 사용)
- [X] **언어 감지 테스트 (Live API)**: 다양한 언어 입력에 대해 `process_input` 메서드가 별도 `genai` 클라이언트를 사용하여 API를 호출하고, 반환된 `ParsedInput` 객체의 `original_language` 필드에 올바른 언어 코드(ko, en, ja, fr, zh 등)를 저장하는지 확인합니다.
- [X] **영어 번역 테스트 (Live API, 한국어)**: 한국어 입력 시, 언어 감지 후 번역 API가 호출되고, 반환된 `ParsedInput` 객체의 `english_text` 필드에 번역된 영어 텍스트가 저장되는지 확인합니다.
- [X] **영어 번역 테스트 (Live API, 다른 언어)**: 한국어 외 다른 언어(예: 일본어, 프랑스어) 입력 시, 번역 API가 호출되고 영어 번역 결과가 저장되는지 확인합니다.
- [X] **영어 번역 테스트 (Live API, 영어 입력)**: 영어 입력 시, 번역 API가 호출되지 않고 `english_text` 필드에 원본 영어 텍스트가 그대로 저장되는지 확인합니다.
- [ ] **영어 번역 테스트 (Live API, 번역 오류)**: 번역 API 호출 중 오류 발생 시, `english_text` 필드에 원본 텍스트가 유지되는지 확인합니다 (오류 로깅 확인).
- [X] **의도/엔티티/도메인 분석 테스트 (Live API, 명확한 요청)**: "파이썬으로 간단한 웹 서버 만드는 코드 짜줘"와 같은 명확한 요청에 대해 분석 API가 호출되고, 반환된 `ParsedInput` 객체에 예상되는 의도(`code_generation`), 엔티티(예: `{"language": "python", "topic": "web server"}`), 도메인(`coding`)이 저장되는지 확인합니다.
- [X] **의도/엔티티/도메인 분석 테스트 (Live API, 일반 질문)**: "오늘 날씨 어때?"와 같은 일반 질문에 대해 분석 API가 호출되고, 예상되는 의도(`question_answering`), 엔티티(예: `{"topic": "weather"}`), 도메인(`general`)이 저장되는지 확인합니다.
- [X] **의도/엔티티/도메인 분석 테스트 (Live API, 비영어 입력)**: 한국어 입력("대한민국의 수도는 어디인가요?")에 대해 번역 후 분석 API가 호출되고, 예상되는 의도(`question_answering`), 엔티티(예: `{"topic": "capital of South Korea"}`), 도메인(`general`)이 저장되는지 확인합니다.
- [X] **의도/엔티티/도메인 분석 테스트 (Live API, 분석 오류)**: 분석 API 호출 중 오류 발생 시, `intent`, `entities`, `domain` 필드가 `None`으로 유지되는지 확인합니다 (오류 로깅 확인).
- [X] **의도/엔티티/도메인 분석 테스트 (Live API, JSON 파싱 오류)**: 분석 API가 유효하지 않은 JSON 형식으로 응답했을 때, `intent`, `entities`, `domain` 필드가 `None`으로 유지되는지 확인합니다 (오류 로깅 확인).
- [X] **최종 반환 객체 테스트 (Live API 통합)**: `process_input` 메서드가 모든 처리(언어 감지, 번역, 분석)를 거친 후 최종적으로 올바른 값들이 포함된 `ParsedInput` 객체를 반환하는지 확인합니다. (기존 `test_process_input_language_detection_and_translation_live` 테스트에 분석 결과 검증 추가하여 통합)

## 3. 에이전트 라우팅 계층 (MCP/Dispatcher) 테스트

### 3.1. `JarvisDispatcher` 클래스 정의 테스트
- [X] `src/jarvis/core/dispatcher.py` 파일에 `JarvisDispatcher` 클래스가 정의되어 있고 `LlmAgent`를 상속하는지 확인
- [X] `JarvisDispatcher` 인스턴스 생성 시 오류가 없는지 확인
- [X] 생성된 인스턴스의 `name` 속성이 "JarvisDispatcher"인지 확인
- [X] 생성된 인스턴스의 `description` 속성이 설정된 설명과 일치하는지 확인
- [X] 생성된 인스턴스의 `model` 속성이 "gemini-2.0-flash-exp"인지 확인 (LlmConfig 제거 후 확인)
- [X] 생성된 인스턴스의 `input_parser` 속성이 `InputParserAgent`의 인스턴스인지 확인
- [X] 생성된 인스턴스의 `sub_agents` 속성이 빈 딕셔너리(`{}`)인지 확인

### 3.2. `JarvisDispatcher.register_agent` 메서드 테스트
- [X] 유효한 `LlmAgent` 인스턴스를 성공적으로 등록하는지 확인 (`sub_agents` 딕셔너리에 추가되는지 검증)
- [X] 등록 시 콘솔에 "Agent '{agent.name}' registered successfully." 메시지가 출력되는지 확인 (캡처 또는 Mock 사용)
- [X] `LlmAgent`가 아닌 다른 타입의 객체를 등록 시 `TypeError`가 발생하는지 확인
- [X] `name` 속성이 없는 에이전트 인스턴스 등록 시 `ValueError`가 발생하는지 확인
- [X] 동일한 이름의 에이전트를 다시 등록할 때 기존 에이전트를 덮어쓰는지 확인 (`sub_agents` 내용 변경 검증)
- [X] 동일한 이름의 에이전트를 다시 등록할 때 콘솔에 "Warning: Agent with name '{agent.name}' already registered. Overwriting." 경고 메시지가 출력되는지 확인 (캡처 또는 Mock 사용)

### 3.3. `JarvisDispatcher.process_request` 메서드 테스트
- [X] `process_request` 메서드가 비동기 함수(`async def`)로 정의되어 있는지 확인
- [X] `process_request` 메서드가 `user_input` 인자를 문자열(`str`) 타입으로 받는지 확인 (타입 힌트 검증)
