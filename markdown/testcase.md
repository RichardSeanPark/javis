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
- [X] 생성된 인스턴스의 `model` 속성이 설정된 모델 이름과 일치하는지 확인 (기본값 또는 생성 시 지정된 값)
- [X] 생성된 인스턴스의 `input_parser` 속성이 `InputParserAgent`의 인스턴스인지 확인
- [X] 생성된 인스턴스의 `sub_agents` 속성이 빈 딕셔너리(`{}`)인지 확인
- [X] 생성된 인스턴스의 `llm_clients` 딕셔너리가 존재하고, 디스패처 모델에 대한 클라이언트가 초기화되었는지 확인

### 3.2. `JarvisDispatcher.register_agent` 메서드 테스트
- [X] 유효한 `LlmAgent` 인스턴스를 성공적으로 등록하는지 확인 (`sub_agents` 딕셔너리와 `tools` 리스트에 추가되는지 검증)
- [X] 등록 시 콘솔에 로그 메시지가 출력되는지 확인
- [X] `LlmAgent`가 아닌 다른 타입의 객체를 등록 시 `TypeError`가 발생하는지 확인
- [X] `name` 속성이 없는 에이전트 인스턴스 등록 시 `ValueError`가 발생하는지 확인
- [X] 동일한 이름의 에이전트를 다시 등록할 때 기존 에이전트를 덮어쓰고 `tools` 리스트도 업데이트하는지 확인
- [X] 동일한 이름의 에이전트를 다시 등록할 때 콘솔에 경고 로그 메시지가 출력되는지 확인

### 3.3. `JarvisDispatcher.process_request` 메서드 테스트
- [X] `process_request` 메서드가 비동기 함수(`async def`)로 정의되어 있는지 확인
- [X] `process_request` 메서드가 `user_input` 인자를 문자열(`str`) 타입으로 받는지 확인 (타입 힌트 검증)
- [ ] `process_request` 내부에서 `self.input_parser.process_input` 메서드가 `user_input` 인자와 함께 비동기적으로 호출되는지 확인 (Mock 사용)
- [ ] `self.input_parser.process_input` 호출 결과(Mock 객체)가 `parsed_input` 변수에 할당되는지 확인
- [ ] `process_request` 실행 후 `dispatcher.current_parsed_input`에 `input_parser.process_input`의 반환값(Mock 객체)이 할당되는지 확인
- [ ] `process_request` 실행 후 `dispatcher.current_original_language`에 Mock `ParsedInput` 객체의 `original_language` 속성값이 할당되는지 확인

### 3.3.1. 규칙 기반 라우팅 테스트 (현재 미사용)
- [ ] `intent`가 'code_generation'일 때, `CodingAgent`가 등록되어 있다면 해당 에이전트가 선택되는지 확인 (Mock `ParsedInput`, Mock `sub_agents` 사용)
- [ ] `domain`이 'coding'일 때, `CodingAgent`가 등록되어 있다면 해당 에이전트가 선택되는지 확인 (Mock 사용)
- [ ] `intent`가 'question_answering'일 때, `KnowledgeQA_Agent`가 등록되어 있다면 해당 에이전트가 선택되는지 확인 (Mock 사용)
- [ ] `domain`이 'general'일 때, `KnowledgeQA_Agent`가 등록되어 있다면 해당 에이전트가 선택되는지 확인 (Mock 사용)
- [ ] `intent`와 `domain`이 등록된 에이전트와 일치하지 않을 때, `selected_agent`가 `None`인지 확인 (Mock 사용)
- [ ] 해당 `intent`/`domain`에 맞는 에이전트가 `sub_agents`에 등록되어 있지 않을 때, `selected_agent`가 `None`인지 확인 (Mock 사용)
- [ ] `current_parsed_input`이 `None`일 때, 에이전트 선택 로직을 건너뛰는지 확인

### 3.3.2. ADK 자동 위임 설정 테스트 (Live API)
- [X] `JarvisDispatcher` 초기화 시 `instruction` 속성이 올바르게 설정되는지 확인 (위임 관련 키워드 포함)
- [X] `register_agent` 호출 시 전달된 에이전트가 `self.sub_agents` 딕셔너리와 `self.tools` 리스트 양쪽에 추가되는지 확인
- [X] 동일한 이름의 에이전트를 다시 `register_agent`로 등록할 때, 기존 에이전트가 `self.tools` 리스트에서 제거되고 새 에이전트가 추가되는지 확인
- [X] `process_request` 내부에서 디스패처 LLM(`generate_content_async`)이 호출될 때, 동적으로 생성된 프롬프트(instruction + tools + query)가 전달되는지 확인 (로깅 확인)
- [X] **위임 성공 테스트 (CodingAgent)**: 코딩 관련 요청 시, 디스패처 LLM이 "CodingAgent"를 반환하고, 최종 응답 문자열에 "Delegating task to agent: CodingAgent"가 포함되는지 확인 (Live API)
- [X] **위임 성공 테스트 (KnowledgeQA_Agent)**: 일반 질문 시, 디스패처 LLM이 "KnowledgeQA_Agent"를 반환하고, 최종 응답 문자열에 "Delegating task to agent: KnowledgeQA_Agent"가 포함되는지 확인 (Live API)
- [X] **위임 실패 테스트 (적절한 에이전트 없음)**: 등록된 에이전트가 처리할 수 없는 요청 시, 디스패처 LLM이 "NO_AGENT" 또는 관련 없는 에이전트 이름을 반환하고, 최종 응답 문자열에 "No suitable agent found"가 포함되는지 확인 (Live API)

### 3.3.3. A2A 동적 검색 로직 테스트 (Placeholder)
- [X] **A2A 플레이스홀더 진입 테스트 (Mock)**: 디스패처 LLM이 "NO_AGENT"를 반환하도록 Mocking하고, `process_request` 실행 시 A2A 플레이스홀더 블록 내의 로그("Checking A2A Hub (Placeholder)")가 출력되는지 확인.
- [X] **A2A 플레이스홀더 후 반환 메시지 테스트 (Mock)**: 디스패처 LLM이 "NO_AGENT"를 반환하도록 Mocking하고, `process_request`가 최종적으로 "No suitable internal or external agent found to handle the request." 메시지를 반환하는지 확인.
- [-] **A2A 실제 검색/호출 테스트**: (7단계에서 구현 예정)

## 4. 도메인별 에이전트 모듈 계층 테스트

### 4.1. 코딩 에이전트 (`CodingAgent`) 테스트
- [X] `src/jarvis/agents/coding_agent.py` 파일이 존재하는지 확인
- [X] `CodingAgent` 클래스가 `LlmAgent`를 상속하는지 확인
- [X] `CodingAgent` 인스턴스 생성 시 오류가 없는지 확인 (기본값 사용)
- [X] 생성된 인스턴스의 `name` 속성이 "CodingAgent"인지 확인
- [X] 생성된 인스턴스의 `description` 속성이 설정된 설명과 일치하는지 확인
- [X] 생성된 인스턴스의 `model` 속성이 설정된 모델 이름(기본값 `gemini-1.5-flash-latest` 또는 환경변수)과 일치하는지 확인
- [X] 생성된 인스턴스의 `instruction` 속성이 정의된 기본 지침과 일치하는지 확인
- [X] `__init__`에 `name`, `description`, `model` 인자를 전달하여 인스턴스 생성 시 해당 속성이 올바르게 설정되는지 확인
- [-] **툴 등록 테스트**: (5단계에서 툴 구현 후) 코드 실행기 툴이 `__init__`에서 `tools` 리스트에 추가되는지 확인
- [-] **기본 동작 테스트 (Mock)**: (툴 구현 후) 간단한 코딩 요청 시 LLM이 예상되는 지침 및 입력으로 호출되는지 확인 (Mock 사용)
- [-] **기본 동작 테스트 (Live API)**: (툴 구현 후) 간단한 코딩 요청 시 예상되는 코드 생성 결과 또는 설명이 반환되는지 확인 (Live API, 선택적)

### 4.2. 지식 QA 에이전트 (`KnowledgeQA_Agent`) 테스트
- [-] (구현 예정)
- [X] `src/jarvis/agents/qa_agent.py` 파일이 존재하는지 확인
- [X] `KnowledgeQA_Agent` 클래스가 `LlmAgent`를 상속하는지 확인
- [X] `KnowledgeQA_Agent` 인스턴스 생성 시 오류가 없는지 확인 (기본값 사용)
- [X] 생성된 인스턴스의 `name` 속성이 "KnowledgeQA_Agent"인지 확인
- [X] 생성된 인스턴스의 `description` 속성이 설정된 설명과 일치하는지 확인
- [X] 생성된 인스턴스의 `model` 속성이 설정된 모델 이름(기본값 `gemini-1.5-flash-latest` 또는 환경변수)과 일치하는지 확인
- [X] 생성된 인스턴스의 `instruction` 속성이 정의된 기본 지침과 일치하는지 확인
- [X] `__init__`에 `name`, `description`, `model` 인자를 전달하여 인스턴스 생성 시 해당 속성이 올바르게 설정되는지 확인
- [-] **툴 등록 테스트**: (5단계에서 툴 구현 후) 웹 검색 툴이 `__init__`에서 `tools` 리스트에 추가되는지 확인
- [-] **기본 동작 테스트 (Mock)**: (툴 구현 후) 간단한 질문 시 LLM이 예상되는 지침 및 입력으로 호출되는지 확인 (Mock 사용)
- [-] **기본 동작 테스트 (Live API)**: (툴 구현 후) 간단한 질문 시 예상되는 답변이 반환되는지 확인 (Live API, 선택적)
- [-] **웹 검색 툴 사용 테스트 (Mock)**: 최신 정보가 필요한 질문 시, 웹 검색 툴이 호출되는지 확인 (Mock 사용)
- [-] **웹 검색 툴 사용 테스트 (Live API)**: (툴 구현 후) 최신 정보가 필요한 질문 시, 웹 검색 툴을 사용하여 답변을 생성하는지 확인 (Live API, 선택적)

### 4.3. Dispatcher에 에이전트 등록 테스트
- [-] (구현 예정)
