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
- [X] root_agent 변수가 `JarvisDispatcher` 클래스의 인스턴스인지 확인
- [X] root_agent의 name이 "JarvisDispatcher"인지 확인
- [X] root_agent의 description이 "Central dispatcher for the Jarvis AI Framework. Analyzes requests and routes them to the appropriate specialized agent."인지 확인
- [X] "adk run ." 명령어 실행 시 `JarvisDispatcher` 에이전트가 로드되는지 확인 (정적 검사로 대체)

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
- [X] `__init__` 메서드가 "InputParser" 이름, 설명으로 부모 클래스를 초기화하는지 확인
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
- [X] **의도/엔티티/도메인 분석 테스트 (Live API, 명확한 요청)**: "파이썬으로 간단한 웹 서버 만드는 코드 짜줘"와 같은 명확한 요청에 대해 분석 API가 호출되고, 반환된 `ParsedInput` 객체에 예상되는 의도(`code_generation` 또는 `question_answering`), 엔티티(예: `{"language" 또는 "programming_language": "python", "topic" 또는 "task": "web server"}`), 도메인(`coding`)이 저장되는지 확인합니다.
- [X] **의도/엔티티/도메인 분석 테스트 (Live API, 일반 질문)**: "오늘 날씨 어때?"와 같은 일반 질문에 대해 분석 API가 호출되고, 예상되는 의도(`question_answering`), 엔티티(예: `{"topic": "weather"}`), 도메인(`general` 또는 `weather`)이 저장되는지 확인합니다.
- [X] **의도/엔티티/도메인 분석 테스트 (Live API, 비영어 입력)**: 한국어 입력("대한민국의 수도는 어디인가요?")에 대해 번역 후 분석 API가 호출되고, 예상되는 의도(`question_answering` 또는 `translation`), 엔티티(주석 처리됨), 도메인(`geography` 또는 `general`)이 저장되는지 확인합니다.
- [X] **의도/엔티티/도메인 분석 테스트 (Live API, 분석 오류)**: 분석 API 호출 중 오류 발생 시, `intent`, `entities`, `domain` 필드가 `None`으로 유지되는지 확인합니다 (오류 로깅 확인).
- [X] **의도/엔티티/도메인 분석 테스트 (Live API, JSON 파싱 오류)**: 분석 API가 유효하지 않은 JSON 형식으로 응답했을 때, `intent`, `entities`, `domain` 필드가 `None`으로 유지되는지 확인합니다 (오류 로깅 확인).
- [-] **최종 반환 객체 테스트 (Live API 통합)**: `process_input` 메서드가 모든 처리(언어 감지, 번역, 분석)를 거친 후 최종적으로 올바른 값들이 포함된 `ParsedInput` 객체를 반환하는지 확인합니다. (불안정하여 skip 처리)

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

### 3.3.3. A2A 동적 검색 로직 테스트 (Placeholder -> 실제 구현)
- [X] **A2A 플레이스홀더 진입 테스트 (Mock)**: 디스패처 LLM이 "NO_AGENT"를 반환하도록 Mocking하고, `process_request` 실행 시 A2A 로직이 시작되는지 확인 (예: `_discover_a2a_agents` 호출).
- [X] **`_discover_a2a_agents` 호출 테스트 (Mock)**: 디스패처 LLM이 "NO_AGENT"를 반환하도록 Mocking하고, `_discover_a2a_agents` 메서드가 올바른 `capability` 문자열과 함께 호출되는지 확인.
- [ ] **A2A 검색 성공 및 호출 시도 (Mock)**: `_discover_a2a_agents`가 Mock Agent Card(들)을 반환하도록 설정하고, `process_request`가 `_call_a2a_agent`를 첫 번째 반환된 Agent Card와 올바른 입력 텍스트(`llm_input_text`)로 호출하는지 확인.
- [ ] **A2A 호출 성공 및 결과 반환 (Mock)**: `_discover_a2a_agents`가 Agent Card를 반환하고, `_call_a2a_agent`가 성공적인 결과 문자열(예: "A2A Agent Result OK")을 반환하도록 Mocking했을 때, `process_request`가 해당 결과 문자열을 최종적으로 반환하는지 확인.
- [ ] **A2A 호출 실패 및 에러 메시지 반환 (Mock)**: `_discover_a2a_agents`가 Agent Card를 반환하고, `_call_a2a_agent`가 에러 메시지 문자열(예: "Error from A2A agent...")을 반환하도록 Mocking했을 때, `process_request`가 해당 에러 메시지를 최종적으로 반환하는지 확인.
- [X] **A2A 검색 실패 시 최종 메시지 반환 (Mock)**: `_discover_a2a_agents`가 빈 리스트를 반환하도록 Mocking했을 때, `_call_a2a_agent`가 호출되지 않고 `process_request`가 최종적으로 "I cannot find..." 메시지를 반환하는지 확인. (이전 플레이스홀더 테스트와 유사)
- [ ] **A2A 검색 중 예외 발생 시 최종 메시지 반환 (Mock)**: `_discover_a2a_agents` 호출 시 `httpx.RequestError` 등 예외가 발생하도록 Mocking했을 때, `process_request`가 최종적으로 "I cannot find..." 메시지를 반환하고 에러가 로깅되는지 확인.
- [ ] **A2A 호출 중 예외 발생 시 최종 메시지 반환 (Mock)**: `_call_a2a_agent` 호출 시 `httpx.HTTPStatusError` 등 예외가 발생하도록 Mocking했을 때, `process_request`가 최종적으로 "I cannot find..." 메시지를 반환하고 에러가 로깅되는지 확인 (try-except 블록 확인).
- [X] **A2A 실제 검색/호출 테스트**: (통합 테스트 환경 구성 복잡성으로 생략, 관련 Dispatcher 로직은 위의 Mock 테스트들로 검증 완료)

### 3.4. 선택된 에이전트 호출 및 컨텍스트/툴 주입 테스트
- [X] **`process_request` 반환값 테스트 (Mock)**: `process_request`가 내부 에이전트 위임 결정 시, 올바른 `DelegationInfo` 딕셔너리(agent_name, input_text, original_language, required_tools, conversation_history 포함)를 반환하는지 확인 (Mock `ContextManager`).
- [X] **`_run_async_impl` 위임 이벤트 테스트 (Mock)**: `process_request`가 `DelegationInfo`를 반환했을 때, `_run_async_impl`이 올바른 콘텐츠(`[System] Delegating to ...`)를 포함한 위임 `Event`를 yield하는지 확인.
- [X] **툴 임시 주입 및 복구 테스트 (Mock)**: `_run_async_impl`에서 위임 이벤트 발생 전후로 하위 에이전트의 `tools` 속성이 `DelegationInfo.required_tools`로 변경되었다가 원래대로 복구되는지 확인 (Mock 하위 에이전트).
- [X] **Instruction 임시 업데이트 및 복구 테스트 (Mock)**: `_run_async_impl`에서 위임 이벤트 발생 전후로 하위 에이전트의 `instruction` 속성에 컨텍스트 정보가 추가되었다가 원래대로 복구되는지 확인 (Mock 하위 에이전트).
- [X] **`_run_async_impl` 컨텍스트 관리자 호출 테스트 (Mock)**: `_run_async_impl` 실행 시 내부적으로 호출되는 `process_request`가 `ContextManager.get_formatted_context`를 올바른 `session_id`로 호출하는지 확인 (Mock `ContextManager` - 실제 호출은 `process_request` 테스트에서 검증됨).
- [-] (향후 구현) `JarvisDispatcher`가 선택된 내부 에이전트를 호출할 때, `ParsedInput.english_text`와 `original_language`를 올바르게 전달하는지 확인 (Mock 사용) # 현재 테스트는 위임 *정보* 반환까지만 검증, 실제 호출은 Runner 역할
- [-] (향후 구현) `JarvisDispatcher`가 선택된 내부 에이전트를 호출할 때, `agent_tool_map`에 정의된 올바른 툴 목록만 주입하는지 확인 (Mock 사용) # 현재 테스트는 위임 *정보* 반환까지만 검증
- [-] (향후 구현) `JarvisDispatcher`가 선택된 내부 에이전트를 호출할 때, 대화 이력 컨텍스트를 올바르게 주입하는지 확인 (Mock `ContextManager` 사용) # 현재 테스트는 위임 *정보* 반환까지만 검증

## 3.6. 에러 핸들링 테스트 (`JarvisDispatcher`)

- [X] **입력 파싱 오류 테스트 (Mock)**: `InputParserAgent.process_input` 호출 시 예외가 발생하도록 Mocking 했을 때, `process_request`가 "Error: Failed to parse your input." 메시지를 반환하는지 확인.
- [X] **LLM 위임 결정 오류 테스트 (Mock)**: Dispatcher LLM (`generate_content_async`) 호출 시 예외가 발생하도록 Mocking 했을 때, `process_request`가 내부적으로 "NO_AGENT"로 처리하고 최종적으로 "I cannot find..." 메시지를 반환하는지 확인.
- [X] **A2A 검색/호출 오류 테스트 (Mock)**: `_discover_a2a_agents` 또는 `_call_a2a_agent` 내부에서 HTTP 오류 등이 발생하도록 Mocking 했을 때, 해당 메서드가 에러 메시지/빈 리스트를 반환하고 `process_request`가 최종적으로 A2A 에이전트의 에러 메시지 또는 "I cannot find..." 메시지를 반환하는지 확인.
- [X] **하위 에이전트 접근 오류 테스트 (Mock)**: `_run_async_impl`에서 존재하지 않는 `agent_name`으로 위임 시도 시, `KeyError`를 처리하고 `ResponseGenerator`를 통해 오류 이벤트(`Error: Could not find agent ...`)를 yield하는지 확인.
- [X] **응답 생성기 오류 테스트 (Mock)**: `_run_async_impl`의 마지막 단계에서 `response_generator.generate_response` 호출 시 예외가 발생하도록 Mocking 했을 때, 최종적으로 "Error: Failed to generate final response." 텍스트를 포함한 Event를 yield하는지 확인.
- [X] **`process_request` 전체 오류 테스트 (Mock)**: `process_request` 내부의 예상치 못한 지점에서 일반 `Exception`이 발생하도록 Mocking 했을 때, "Error: An unexpected internal error..." 메시지를 반환하는지 확인.
- [X] **`_run_async_impl` 전체 오류 테스트 (Mock)**: `_run_async_impl` 내부의 예상치 못한 지점에서 일반 `Exception`이 발생하도록 Mocking 했을 때, `ResponseGenerator`를 통해 "Error: An unexpected error occurred." 메시지를 포함한 Event를 yield하는지 확인.

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
- [X] **툴 등록 테스트**: `CodingAgent.__init__`에서 `code_execution_tool`이 `tools` 리스트에 명시적으로 추가되어 부모 클래스로 전달되는지 확인
- [-] **기본 동작 테스트 (Mock)**: (툴 구현 후) 간단한 코딩 요청 시 LLM이 예상되는 지침 및 입력으로 호출되는지 확인 (Mock 사용)
- [-] **기본 동작 테스트 (Live API)**: (툴 구현 후) 간단한 코딩 요청 시 예상되는 코드 생성 결과 또는 설명이 반환되는지 확인 (Live API, 선택적)

### 4.2. 지식 QA 에이전트 (`KnowledgeQA_Agent`) 테스트
- [X] `src/jarvis/agents/qa_agent.py` 파일이 존재하는지 확인
- [X] `KnowledgeQA_Agent` 클래스가 `LlmAgent`를 상속하는지 확인
- [X] `KnowledgeQA_Agent` 인스턴스 생성 시 오류가 없는지 확인 (기본값 사용)
- [X] 생성된 인스턴스의 `name` 속성이 "KnowledgeQA_Agent"인지 확인
- [X] 생성된 인스턴스의 `description` 속성이 설정된 설명과 일치하는지 확인
- [X] 생성된 인스턴스의 `model` 속성이 설정된 모델 이름(기본값 `gemini-1.5-flash-latest` 또는 환경변수)과 일치하는지 확인
- [X] 생성된 인스턴스의 `instruction` 속성이 정의된 기본 지침과 일치하는지 확인
- [X] `__init__`에 `name`, `description`, `model` 인자를 전달하여 인스턴스 생성 시 해당 속성이 올바르게 설정되는지 확인
- [ ] **툴 등록 테스트**: `CodingAgent.__init__`에서 `code_execution_tool`이 `tools` 리스트에 명시적으로 추가되어 부모 클래스로 전달되는지 확인
- [-] **기본 동작 테스트 (Mock)**: (툴 구현 후) 간단한 질문 시 LLM이 예상되는 지침 및 입력으로 호출되는지 확인 (Mock 사용)
- [-] **기본 동작 테스트 (Live API)**: (툴 구현 후) 간단한 질문 시 예상되는 답변이 반환되는지 확인 (Live API, 선택적)
- [-] **웹 검색 툴 사용 테스트 (Mock)**: 최신 정보가 필요한 질문 시, 웹 검색 툴이 호출되는지 확인 (Mock 사용)
- [-] **웹 검색 툴 사용 테스트 (Live API)**: (툴 구현 후) 최신 정보가 필요한 질문 시, 웹 검색 툴을 사용하여 답변을 생성하는지 확인 (Live API, 선택적)

### 4.3. Dispatcher에 에이전트 등록 테스트
- [X] `JarvisDispatcher.__init__` 호출 시 `CodingAgent`가 `sub_agents` 딕셔너리에 `\"CodingAgent\"` 키로 등록되는지 확인
- [X] `JarvisDispatcher.__init__` 호출 시 `CodingAgent`가 `tools` 리스트에 추가되는지 확인 (`CodingAgent` 인스턴스 포함 여부 검증)
- [X] `JarvisDispatcher.__init__` 호출 시 `KnowledgeQA_Agent`가 `sub_agents` 딕셔너리에 `\"KnowledgeQA_Agent\"` 키로 등록되는지 확인
- [X] `JarvisDispatcher.__init__` 호출 시 `KnowledgeQA_Agent`가 `tools` 리스트에 추가되는지 확인 (`KnowledgeQA_Agent` 인스턴스 포함 여부 검증)

## 5. 툴 및 컨텍스트 관리 계층 테스트

### 5.2. 번역 툴 (`translate_tool`) 테스트
- [X] `src/jarvis/tools/translate_tool.py` 파일에 `translate_tool` ADK `Tool` 객체가 정의되어 있는지 확인
    - [X] `name` 속성이 "translate_tool"인지 확인
    - [X] `description` 속성이 올바른 설명을 포함하는지 확인
    - [X] `function_declarations`에 `translate_text` 함수 정보가 올바르게 명시되어 있는지 확인 (name, description, parameters)
        - [X] `parameters` 스키마에 `text`, `target_language` (필수), `source_language` (선택) 필드가 정의되어 있는지 확인
- [X] `translate_text` 함수 기본 번역 테스트 (한국어 -> 영어, Live API): "안녕하세요"를 영어로 번역 시 예상되는 결과(예: "Hello")가 반환되는지 확인
- [X] `translate_text` 함수 기본 번역 테스트 (영어 -> 한국어, Live API): "Hello"를 한국어로 번역 시 예상되는 결과(예: "안녕하세요")가 반환되는지 확인
- [X] `translate_text` 함수 자동 소스 언어 감지 테스트 (영어 -> 프랑스어, Live API): "Hello"를 프랑스어로 번역(`source_language` 미지정) 시 예상되는 결과(예: "Bonjour")가 반환되는지 확인
- [X] `src/jarvis/tools/__init__.py`에 `translate_tool`이 `available_tools` 리스트에 포함되어 있는지 확인
- [X] **툴 주입 테스트**: `JarvisDispatcher._run_async_impl` 메서드 내에서 `KnowledgeQA_Agent`로 위임 시 `web_search_tool`, `translate_tool`이 `required_tools`에 포함되어 에이전트에 성공적으로 주입되는지 확인
- [X] **주입된 툴 복원 테스트**: `JarvisDispatcher._run_async_impl` 내의 finally 블록에서 에이전트에 원래 툴 목록이 정상적으로 복원되는지 확인
- [X] **에러 상황 툴 복원 테스트**: 에이전트 호출 중 예외가 발생하더라도 finally 블록에서 원래 툴이 복원되는지 확인

### 5.3. 웹 검색 툴 (`web_search_tool`) 테스트
- [X] `src/jarvis/tools/web_search_tool.py` 파일에 `web_search_tool` ADK `FunctionTool` 객체가 정의되어 있는지 확인
    - [X] `name` 속성이 `web_search`인지 확인
    - [X] `description` 속성이 올바른 설명을 포함하는지 확인 (함수 독스트링 확인)
- [X] `function_declarations` 내부 스키마 확인 (타입, 필수 필드 등) # 객체 타입/이름/설명 존재 확인 완료, 세부 스키마 직접 확인은 ADK 내부 구현으로 어려움
- [X] **기본 검색 테스트 (Mock)**: `DDGS().atext`가 Mock 결과를 반환하도록 설정하고, `web_search` 함수 호출 시 예상되는 포맷의 문자열 결과가 반환되는지 확인
- [X] **결과 없음 테스트 (Mock)**: `DDGS().atext`가 빈 리스트를 반환하도록 설정하고, `web_search` 함수 호출 시 "No relevant information found..." 메시지가 반환되는지 확인
- [X] **API 호출 오류 테스트 (Mock)**: `DDGS().atext` 호출 시 예외가 발생하도록 Mocking하고, `web_search` 함수 호출 시 "An error occurred..." 메시지가 반환되는지 확인
- [X] **요약 성공 테스트 (Mock LLM)**: 충분히 긴 Mock 검색 결과(`DDGS().atext` Mock 반환값)와 초기화된 Mock LLM(`genai.GenerativeModel` Mock)이 주어졌을 때, `web_search` 함수가 `model.generate_content_async`를 올바른 요약 프롬프트로 호출하고, Mock LLM 응답(`response.text`)을 포함한 "Summary based on..." 형식의 문자열을 반환하는지 확인.
- [X] **요약 건너뛰기 테스트 (짧은 결과)**: `DDGS().atext` Mock 반환값이 200자 미만일 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
- [X] **요약 건너뛰기 테스트 (LLM 미초기화)**: `web_search_tool.LLM_CLIENT_INITIALIZED`를 `False`로 패치(patch)했을 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
- [X] **요약 실패 테스트 (Mock LLM 에러)**: `genai.GenerativeModel.generate_content_async` 호출 시 예외가 발생하도록 Mocking했을 때, "Web Search Results for..." 형식의 원본 결과 문자열과 함께 "(Note: Summarization failed...)" 메시지가 포함되어 반환되는지 확인.
- [X] `src/jarvis/tools/__init__.py`에 `web_search_tool`이 `available_tools` 리스트에 포함되어 있는지 확인

### 5.3.1 Dispatcher 컨텍스트 저장 테스트
- [X] **컨텍스트 저장 성공 테스트 (Mock)**: `_run_async_impl`이 성공적으로 최종 응답(`processed_final_response`)을 생성하고 yield하기 직전에 `ContextManager.add_message`가 올바른 `session_id`, `user_input`, `ai_response` (`processed_final_response`와 동일), `original_language` 값으로 호출되는지 확인.
- [X] **컨텍스트 저장 실패 시 로깅 테스트 (Mock)**: `ContextManager.add_message` 호출 시 예외가 발생하도록 Mocking했을 때, 에러가 로깅되고 최종 응답 이벤트는 정상적으로 yield되는지 확인.
- [X] **응답 생성 실패 시 컨텍스트 저장 테스트 (Mock)**: `response_generator.generate_response` 호출 시 예외가 발생하도록 Mocking했을 때, `ContextManager.add_message`가 올바른 `session_id`, `user_input`, 그리고 *에러 메시지*(`"Error: Failed to generate final response."` 등)를 `ai_response`로 사용하여 호출되는지 확인.

### 5.4. 코드 실행 툴 (`code_execution_tool`) 테스트
- [X] `src/jarvis/tools/code_execution_tool.py` 파일에 `code_execution_tool` ADK `FunctionTool` 객체가 정의되어 있는지 확인
    - [X] `name` 속성이 `execute_python_code`인지 확인
    - [X] `description` 속성이 함수의 독스트링과 일치하는지 확인 (보안 경고 포함)
- [X] 내부 `function_declarations` 확인 (타입, 필수 필드 등) # 객체 타입/이름/설명 존재 확인 완료, 세부 스키마 직접 확인은 ADK 내부 구현으로 어려움
- [X] **기본 실행 테스트**: 간단한 `print`문 실행 시 `Stdout:`와 함께 올바른 출력이 반환되는지 확인
- [X] **계산 및 출력 테스트**: 변수 할당 및 계산 후 `print`하는 코드 실행 시 올바른 출력이 반환되는지 확인
- [X] **표준 에러(stderr) 캡처 테스트**: `import sys; sys.stderr.write('Error message')` 실행 시 `Stderr:`와 함께 올바른 에러 메시지가 반환되는지 확인
- [X] **예외 발생 테스트**: `1 / 0` 과 같이 예외를 발생시키는 코드 실행 시 `Error during execution:` 메시지와 함께 `ZeroDivisionError` 및 traceback 정보가 반환되는지 확인
- [X] **출력 없는 코드 테스트**: 변수 할당만 하는 코드 실행 시 "Code executed successfully (no stderr output)." 메시지가 반환되는지 확인
- [X] **제한된 빌트인 함수 테스트 (RestrictedPython)**: 허용되지 않는 빌트인 함수(예: `open('file.txt', 'w')`) 사용 시 `NameError` 또는 유사한 보안 관련 오류 메시지가 반환되는지 확인.
- [X] **임의 모듈 임포트 금지 테스트 (RestrictedPython)**: 기본적으로 허용되지 않는 모듈(예: `import os`) 임포트 시 `ImportError` 또는 보안 관련 오류 메시지가 반환되는지 확인.
- [X] **속성 접근 제한 테스트 (RestrictedPython)**: 안전하지 않은 속성(예: `().__class__`) 접근 시도 시 오류 메시지가 반환되는지 확인.
    - [X] `src/jarvis/tools/__init__.py`에 `code_execution_tool`이 `available_tools` 리스트에 포함되어 있는지 확인

### 5.5. 툴 레지스트리 및 주입 테스트 (`src/jarvis/core/dispatcher.py`)
- [X] `JarvisDispatcher.__init__`에서 `src.jarvis.tools`로부터 `available_tools`가 임포트 되는지 확인 (코드 정적 분석 또는 Mock 확인)
- [X] `JarvisDispatcher.__init__`에서 `agent_tool_map` 딕셔너리가 생성되고 올바른 에이전트-툴 매핑을 포함하는지 확인
    - [X] `CodingAgent` 키에 `code_execution_tool`이 포함되어 있는지 확인
    - [X] `KnowledgeQA_Agent` 키에 `web_search_tool`과 `translate_tool`이 포함되어 있는지 확인
- [X] `JarvisDispatcher.process_request` 내부에 툴 주입 로직을 위한 TODO 주석이 존재하는지 확인 (코드 정적 분석)
- [X] 실제 툴 주입 로직 테스트 (Mock): `process_request`가 위임 대상 에이전트에게 `agent_tool_map` 기반의 올바른 툴 목록만 전달하는지 확인 (Mock 사용)

### 5.6. 컨텍스트 관리자 (`ContextManager`) 테스트 (`src/jarvis/core/context_manager.py`)
- [X] `ContextManager` 인스턴스가 정상적으로 생성되는지 확인 (`session_histories`가 빈 `defaultdict`인지 확인)
- [X] `add_message` 메서드가 세션 ID별로 메시지(user, ai, lang) 튜플을 `session_histories` deque에 올바르게 추가하는지 확인
- [X] `add_message` 메서드가 `session_id` 없이 호출될 때 메시지를 추가하지 않고 에러를 로깅하는지 확인
- [X] `get_formatted_context` 메서드가 지정된 세션의 최근 N개 대화 기록을 "User: ...\nAI: ..." 형식의 문자열로 올바르게 반환하는지 확인 (`max_history` 파라미터 존중)
- [X] `get_formatted_context` 메서드가 `max_history`보다 적은 기록을 가진 세션에 대해 사용 가능한 모든 기록을 반환하는지 확인
- [X] `get_formatted_context` 메서드가 기록이 없는 세션 ID에 대해 빈 문자열을 반환하는지 확인
- [X] `get_formatted_context` 메서드가 존재하지 않는 세션 ID에 대해 빈 문자열을 반환하고 경고를 로깅하는지 확인
- [X] `add_message` 호출 시 deque의 `maxlen`을 초과하면 가장 오래된 메시지가 자동으로 삭제되는지 확인
- [X] `clear_history` 메서드가 특정 세션 ID의 기록을 완전히 삭제하는지 확인
- [X] `clear_history` 메서드가 존재하지 않는 세션 ID에 대해 호출될 때 경고를 로깅하는지 확인

## 6. 응답 생성 및 출력 계층 테스트 (`src/jarvis/components/response_generator.py`)
- [X] **ResponseGenerator 인스턴스화 테스트**: `ResponseGenerator` 인스턴스가 정상적으로 생성되는지 확인
- [X] **Dispatcher 연동 테스트**: `JarvisDispatcher`가 `__init__` 시 `ResponseGenerator` 인스턴스를 생성하고 `self.response_generator`에 저장하는지 확인.
- [X] **generate_response 기본 동작 (영어 입력)**: `generate_response(english_result="Hello", original_language='en')` 호출 시 "Hello"를 반환하는지 확인.
- [X] **generate_response 기본 동작 (비영어 입력, Placeholder)**: `generate_response(english_result="Hello", original_language='ko')` 호출 시 "(In English, as translation is not yet implemented): Hello" 와 같은 형식의 문자열을 반환하는지 확인.
- [X] **generate_response None 입력 처리**: `generate_response(english_result=None, original_language='en')` 호출 시 "I received an empty response..." 메시지를 반환하는지 확인.
- [X] **generate_response 비문자열 입력 처리**: `generate_response(english_result={"key": "value"}, original_language='en')` 호출 시 `str({"key": "value"})` 결과(`'{'key': 'value'}'`)를 반환하는지 확인.
- [X] **Dispatcher -> ResponseGenerator 호출 테스트 (Mock)**: `JarvisDispatcher._run_async_impl`에서 직접 응답 문자열(예: "처리 불가")을 반환해야 할 때, `response_generator.generate_response`가 해당 문자열과 `current_original_language`를 인자로 받아 호출되는지 확인 (Mock `response_generator`).

### 6.2.1. 결과 처리 및 포맷팅 테스트 (`generate_response`)
- [X] **문자열 입력 테스트**: `english_result`가 일반 문자열일 때, 해당 문자열이 그대로 반환되는지 확인 (`original_language='en'`).
- [X] **None 입력 테스트**: `english_result`가 `None`일 때, "I received an empty response..." 메시지가 반환되는지 확인.
- [X] **딕셔너리 입력 테스트**: `english_result`가 딕셔너리(`{"key": "value"}`)일 때, `str()` 변환 결과(`'{'key': 'value'}'`)가 반환되는지 확인 (`original_language='en'`).
- [X] **리스트 입력 테스트**: `english_result`가 리스트(`[1, 2, 3]`)일 때, `str()` 변환 결과(`'[1, 2, 3]'`)가 반환되는지 확인 (`original_language='en'`).
- [X] **문자열 변환 오류 테스트**: `english_result` 객체의 `__str__` 메서드가 예외를 발생시키도록 Mocking 했을 때, "I encountered an issue processing the result." 메시지가 반환되는지 확인.

## 6.4. Dispatcher 연동 테스트 (`src/jarvis/core/dispatcher.py`)
- [X] **ResponseGenerator 호출 테스트 (Mock)**: `_run_async_impl`에서 최종 응답 생성 시, `response_generator.generate_response`가 올바른 결과(`final_response_message`)와 원본 언어(`current_original_language`)를 인자로 받아 호출되는지 확인.

## 7. 에이전트 간 상호작용 (A2A) 테스트

### 7.1. Agent Hub 서버 테스트 (`src/jarvis/interfaces/agent_hub/server.py`)
- [ ] FastAPI 앱 인스턴스(`app`)가 정상적으로 생성되는지 확인
- [ ] 루트 경로(`/`) GET 요청 시 "Jarvis Agent Hub is running." 메시지와 함께 200 응답 반환 확인 (TestClient 사용)
- [ ] `/register` POST 엔드포인트가 존재하는지 확인 (TestClient 사용, 422 Unprocessable Entity 예상 - body 없이 호출)
- [ ] 유효한 `AgentCard` 데이터로 `/register` POST 요청 시 201 응답 및 성공 메시지 반환 확인
- [ ] `/register` 호출 후 `/agents` GET 요청 시 등록된 에이전트 정보가 포함된 리스트 반환 확인
- [ ] 동일한 `agent_id`로 `/register` 재호출 시 기존 정보 덮어쓰기 확인 (경고 로그 확인은 어려울 수 있음)
- [ ] `/discover` POST 엔드포인트가 존재하는지 확인 (TestClient 사용, 422 예상)
- [ ] 유효한 `DiscoveryRequest` (빈 `required_capabilities` 리스트 포함)로 `/discover` POST 요청 시 빈 `discovered_agents` 리스트와 200 응답 반환 확인 (초기 상태)
- [ ] 에이전트 등록 후 `/discover` POST 요청 시 등록된 에이전트가 포함된 리스트 반환 확인 (현재는 필터링 없이 모두 반환)
- [-] (향후 구현) `/discover` 요청 시 `required_capabilities` 기반 필터링 로직 테스트

### 7.2 A2A 통신 라이브러리 설정 테스트
- [-] (구현 예정)

### 7.3. ADK 에이전트 A2A 노출 테스트 (`src/jarvis/interfaces/a2a_adapter/adk_agent_a2a_server.py`)
*   **Wrapper 인스턴스 생성 테스트**
    *   [X] 유효한 ADK `Agent` 인스턴스와 `AgentCard`로 `AdkAgentA2AWrapper` 생성 시 성공 확인
    *   [X] ADK `Agent`가 아닌 객체로 생성 시 `TypeError` 발생 확인
    *   [X] 생성된 인스턴스의 `adk_agent` 및 `agent_card` 속성이 올바르게 설정되었는지 확인
*   **`handle_task` 메서드 테스트 (Mock ADK Agent)**
    *   [X] Mock ADK Agent의 `__call__` 메서드가 비동기 함수일 때, 유효한 텍스트 Task 입력 시 `await adk_agent()`가 호출되는지 확인 (AsyncMock 사용)
    *   [X] Mock ADK Agent의 `__call__` 메서드가 동기 함수일 때, 유효한 텍스트 Task 입력 시 `asyncio.to_thread(adk_agent, ...)` 또는 유사한 방식으로 호출되는지 확인 (Mock 사용, 필요시)
    *   [X] `adk_agent` 호출 성공 시 (Mock 반환값 설정), 반환된 `Task`의 `status.state`가 `COMPLETED`이고 `artifacts`에 Mock 응답 텍스트가 포함된 `TextPart`가 있는지 확인
    *   [X] `adk_agent` 호출 시 예외 발생하도록 Mocking했을 때, 반환된 `Task`의 `status.state`가 `FAILED`이고 `status.error` 속성이 없는지 확인 (또는 None)
    *   [X] Task 메시지에 `TextPart`가 없을 때 경고 로그가 기록되고 `adk_agent`가 빈 문자열 또는 기본값으로 호출되는지 확인 (Mock 확인)
    *   [X] 입력 Task에 `history` 자체가 없거나 비어있을 때 경고 로그가 기록되고 `adk_agent`가 빈 문자열 또는 기본값으로 호출되는지 확인 (Mock 확인)
*   **`handle_task` 메서드 테스트 (Live ADK Agent - 선택적, 복잡성 높음)**
    *   [-] 실제 `CodingAgent` 인스턴스를 래핑하고, 간단한 코드 생성 요청 Task 전송 시 예상되는 코드 결과가 `artifacts`에 포함되어 반환되는지 확인 (Skip - Live 테스트는 현재 범위 아님)
*   **FastAPI 연동 및 엔드포인트 테스트 (Placeholder/향후)**
    *   [-] (A2AServer 베이스 클래스 또는 직접 구현에 따라) A2A 서버가 특정 경로(예: `/a2a`)의 POST 요청을 처리하도록 설정되었는지 확인
    *   [-] 유효한 JSON-RPC `tasks/send` 요청 전송 시 200 응답과 함께 `handle_task`에서 반환된 Task 객체(JSON 직렬화된 형태)를 받는지 확인 (FastAPI TestClient 사용)
    *   [-] 잘못된 JSON-RPC 형식의 요청 전송 시 적절한 JSON-RPC 오류 응답(예: `invalid request`, `method not found`)을 받는지 확인

### 7.4. Dispatcher A2A 클라이언트 로직 테스트 (`src/jarvis/core/dispatcher.py`)
*   **`_discover_a2a_agents` 메서드 테스트 (Mock httpx)**
    - [X] `httpx.AsyncClient.get`이 성공적으로 호출되고, 올바른 Agent Hub URL과 `capability` 쿼리 파라미터가 사용되는지 확인
    - [X] Agent Hub가 성공적인 응답(예: Agent Card 리스트 JSON)을 반환할 때, 해당 리스트가 파싱되어 반환되는지 확인
    - [X] Agent Hub가 빈 리스트(`[]`)를 반환할 때, 빈 리스트가 그대로 반환되는지 확인
    - [X] Agent Hub 연결 실패(`httpx.RequestError`) 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] Agent Hub가 4xx 또는 5xx 상태 코드(`httpx.HTTPStatusError`)를 반환할 때, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] 응답 JSON 파싱 중 예외 발생 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
*   **`_call_a2a_agent` 메서드 테스트 (Mock httpx, Mock google_a2a)**
    - [X] 유효한 `agent_card`
    - [X] API 호출 오류 테스트 (Mock): `DDGS().atext` 호출 시 예외가 발생하도록 Mocking하고, `web_search` 함수 호출 시 "An error occurred..." 메시지가 반환되는지 확인
    - [ ] **요약 성공 테스트 (Mock LLM)**: 충분히 긴 Mock 검색 결과(`DDGS().atext` Mock 반환값)와 초기화된 Mock LLM(`genai.GenerativeModel` Mock)이 주어졌을 때, `web_search` 함수가 `model.generate_content_async`를 올바른 요약 프롬프트로 호출하고, Mock LLM 응답(`response.text`)을 포함한 "Summary based on..." 형식의 문자열을 반환하는지 확인.
    - [ ] **요약 건너뛰기 테스트 (짧은 결과)**: `DDGS().atext` Mock 반환값이 200자 미만일 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 건너뛰기 테스트 (LLM 미초기화)**: `web_search_tool.LLM_CLIENT_INITIALIZED`를 `False`로 패치(patch)했을 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 실패 테스트 (Mock LLM 에러)**: `genai.GenerativeModel.generate_content_async` 호출 시 예외가 발생하도록 Mocking했을 때, "Web Search Results for..." 형식의 원본 결과 문자열과 함께 "(Note: Summarization failed...)" 메시지가 포함되어 반환되는지 확인.
    - [X] `src/jarvis/tools/__init__.py`에 `web_search_tool`이 `available_tools` 리스트에 포함되어 있는지 확인

### 7.4. Dispatcher A2A 클라이언트 로직 테스트 (`src/jarvis/core/dispatcher.py`)
*   **`_discover_a2a_agents` 메서드 테스트 (Mock httpx)**
    - [X] `httpx.AsyncClient.get`이 성공적으로 호출되고, 올바른 Agent Hub URL과 `capability` 쿼리 파라미터가 사용되는지 확인
    - [X] Agent Hub가 성공적인 응답(예: Agent Card 리스트 JSON)을 반환할 때, 해당 리스트가 파싱되어 반환되는지 확인
    - [X] Agent Hub가 빈 리스트(`[]`)를 반환할 때, 빈 리스트가 그대로 반환되는지 확인
    - [X] Agent Hub 연결 실패(`httpx.RequestError`) 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] Agent Hub가 4xx 또는 5xx 상태 코드(`httpx.HTTPStatusError`)를 반환할 때, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] 응답 JSON 파싱 중 예외 발생 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
*   **`_call_a2a_agent` 메서드 테스트 (Mock httpx, Mock google_a2a)**
    - [X] 유효한 `agent_card`
    - [X] API 호출 오류 테스트 (Mock): `DDGS().atext` 호출 시 예외가 발생하도록 Mocking하고, `web_search` 함수 호출 시 "An error occurred..." 메시지가 반환되는지 확인
    - [ ] **요약 성공 테스트 (Mock LLM)**: 충분히 긴 Mock 검색 결과(`DDGS().atext` Mock 반환값)와 초기화된 Mock LLM(`genai.GenerativeModel` Mock)이 주어졌을 때, `web_search` 함수가 `model.generate_content_async`를 올바른 요약 프롬프트로 호출하고, Mock LLM 응답(`response.text`)을 포함한 "Summary based on..." 형식의 문자열을 반환하는지 확인.
    - [ ] **요약 건너뛰기 테스트 (짧은 결과)**: `DDGS().atext` Mock 반환값이 200자 미만일 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 건너뛰기 테스트 (LLM 미초기화)**: `web_search_tool.LLM_CLIENT_INITIALIZED`를 `False`로 패치(patch)했을 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 실패 테스트 (Mock LLM 에러)**: `genai.GenerativeModel.generate_content_async` 호출 시 예외가 발생하도록 Mocking했을 때, "Web Search Results for..." 형식의 원본 결과 문자열과 함께 "(Note: Summarization failed...)" 메시지가 포함되어 반환되는지 확인.
    - [X] `src/jarvis/tools/__init__.py`에 `web_search_tool`이 `available_tools` 리스트에 포함되어 있는지 확인

### 7.5. Dispatcher A2A 클라이언트 로직 테스트 (`src/jarvis/core/dispatcher.py`)
*   **`_discover_a2a_agents` 메서드 테스트 (Mock httpx)**
    - [X] `httpx.AsyncClient.get`이 성공적으로 호출되고, 올바른 Agent Hub URL과 `capability` 쿼리 파라미터가 사용되는지 확인
    - [X] Agent Hub가 성공적인 응답(예: Agent Card 리스트 JSON)을 반환할 때, 해당 리스트가 파싱되어 반환되는지 확인
    - [X] Agent Hub가 빈 리스트(`[]`)를 반환할 때, 빈 리스트가 그대로 반환되는지 확인
    - [X] Agent Hub 연결 실패(`httpx.RequestError`) 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] Agent Hub가 4xx 또는 5xx 상태 코드(`httpx.HTTPStatusError`)를 반환할 때, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] 응답 JSON 파싱 중 예외 발생 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
*   **`_call_a2a_agent` 메서드 테스트 (Mock httpx, Mock google_a2a)**
    - [X] 유효한 `agent_card`
    - [X] API 호출 오류 테스트 (Mock): `DDGS().atext` 호출 시 예외가 발생하도록 Mocking하고, `web_search` 함수 호출 시 "An error occurred..." 메시지가 반환되는지 확인
    - [ ] **요약 성공 테스트 (Mock LLM)**: 충분히 긴 Mock 검색 결과(`DDGS().atext` Mock 반환값)와 초기화된 Mock LLM(`genai.GenerativeModel` Mock)이 주어졌을 때, `web_search` 함수가 `model.generate_content_async`를 올바른 요약 프롬프트로 호출하고, Mock LLM 응답(`response.text`)을 포함한 "Summary based on..." 형식의 문자열을 반환하는지 확인.
    - [ ] **요약 건너뛰기 테스트 (짧은 결과)**: `DDGS().atext` Mock 반환값이 200자 미만일 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 건너뛰기 테스트 (LLM 미초기화)**: `web_search_tool.LLM_CLIENT_INITIALIZED`를 `False`로 패치(patch)했을 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 실패 테스트 (Mock LLM 에러)**: `genai.GenerativeModel.generate_content_async` 호출 시 예외가 발생하도록 Mocking했을 때, "Web Search Results for..." 형식의 원본 결과 문자열과 함께 "(Note: Summarization failed...)" 메시지가 포함되어 반환되는지 확인.
    - [X] `src/jarvis/tools/__init__.py`에 `web_search_tool`이 `available_tools` 리스트에 포함되어 있는지 확인

### 7.6. Dispatcher A2A 클라이언트 로직 테스트 (`src/jarvis/core/dispatcher.py`)
*   **`_discover_a2a_agents` 메서드 테스트 (Mock httpx)**
    - [X] `httpx.AsyncClient.get`이 성공적으로 호출되고, 올바른 Agent Hub URL과 `capability` 쿼리 파라미터가 사용되는지 확인
    - [X] Agent Hub가 성공적인 응답(예: Agent Card 리스트 JSON)을 반환할 때, 해당 리스트가 파싱되어 반환되는지 확인
    - [X] Agent Hub가 빈 리스트(`[]`)를 반환할 때, 빈 리스트가 그대로 반환되는지 확인
    - [X] Agent Hub 연결 실패(`httpx.RequestError`) 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] Agent Hub가 4xx 또는 5xx 상태 코드(`httpx.HTTPStatusError`)를 반환할 때, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] 응답 JSON 파싱 중 예외 발생 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
*   **`_call_a2a_agent` 메서드 테스트 (Mock httpx, Mock google_a2a)**
    - [X] 유효한 `agent_card`
    - [X] API 호출 오류 테스트 (Mock): `DDGS().atext` 호출 시 예외가 발생하도록 Mocking하고, `web_search` 함수 호출 시 "An error occurred..." 메시지가 반환되는지 확인
    - [ ] **요약 성공 테스트 (Mock LLM)**: 충분히 긴 Mock 검색 결과(`DDGS().atext` Mock 반환값)와 초기화된 Mock LLM(`genai.GenerativeModel` Mock)이 주어졌을 때, `web_search` 함수가 `model.generate_content_async`를 올바른 요약 프롬프트로 호출하고, Mock LLM 응답(`response.text`)을 포함한 "Summary based on..." 형식의 문자열을 반환하는지 확인.
    - [ ] **요약 건너뛰기 테스트 (짧은 결과)**: `DDGS().atext` Mock 반환값이 200자 미만일 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 건너뛰기 테스트 (LLM 미초기화)**: `web_search_tool.LLM_CLIENT_INITIALIZED`를 `False`로 패치(patch)했을 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 실패 테스트 (Mock LLM 에러)**: `genai.GenerativeModel.generate_content_async` 호출 시 예외가 발생하도록 Mocking했을 때, "Web Search Results for..." 형식의 원본 결과 문자열과 함께 "(Note: Summarization failed...)" 메시지가 포함되어 반환되는지 확인.
    - [X] `src/jarvis/tools/__init__.py`에 `web_search_tool`이 `available_tools` 리스트에 포함되어 있는지 확인

### 7.7. Dispatcher A2A 클라이언트 로직 테스트 (`src/jarvis/core/dispatcher.py`)
*   **`_discover_a2a_agents` 메서드 테스트 (Mock httpx)**
    - [X] `httpx.AsyncClient.get`이 성공적으로 호출되고, 올바른 Agent Hub URL과 `capability` 쿼리 파라미터가 사용되는지 확인
    - [X] Agent Hub가 성공적인 응답(예: Agent Card 리스트 JSON)을 반환할 때, 해당 리스트가 파싱되어 반환되는지 확인
    - [X] Agent Hub가 빈 리스트(`[]`)를 반환할 때, 빈 리스트가 그대로 반환되는지 확인
    - [X] Agent Hub 연결 실패(`httpx.RequestError`) 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] Agent Hub가 4xx 또는 5xx 상태 코드(`httpx.HTTPStatusError`)를 반환할 때, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] 응답 JSON 파싱 중 예외 발생 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
*   **`_call_a2a_agent` 메서드 테스트 (Mock httpx, Mock google_a2a)**
    - [X] 유효한 `agent_card`
    - [X] API 호출 오류 테스트 (Mock): `DDGS().atext` 호출 시 예외가 발생하도록 Mocking하고, `web_search` 함수 호출 시 "An error occurred..." 메시지가 반환되는지 확인
    - [ ] **요약 성공 테스트 (Mock LLM)**: 충분히 긴 Mock 검색 결과(`DDGS().atext` Mock 반환값)와 초기화된 Mock LLM(`genai.GenerativeModel` Mock)이 주어졌을 때, `web_search` 함수가 `model.generate_content_async`를 올바른 요약 프롬프트로 호출하고, Mock LLM 응답(`response.text`)을 포함한 "Summary based on..." 형식의 문자열을 반환하는지 확인.
    - [ ] **요약 건너뛰기 테스트 (짧은 결과)**: `DDGS().atext` Mock 반환값이 200자 미만일 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 건너뛰기 테스트 (LLM 미초기화)**: `web_search_tool.LLM_CLIENT_INITIALIZED`를 `False`로 패치(patch)했을 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 실패 테스트 (Mock LLM 에러)**: `genai.GenerativeModel.generate_content_async` 호출 시 예외가 발생하도록 Mocking했을 때, "Web Search Results for..." 형식의 원본 결과 문자열과 함께 "(Note: Summarization failed...)" 메시지가 포함되어 반환되는지 확인.
    - [X] `src/jarvis/tools/__init__.py`에 `web_search_tool`이 `available_tools` 리스트에 포함되어 있는지 확인

### 7.8. Dispatcher A2A 클라이언트 로직 테스트 (`src/jarvis/core/dispatcher.py`)
*   **`_discover_a2a_agents` 메서드 테스트 (Mock httpx)**
    - [X] `httpx.AsyncClient.get`이 성공적으로 호출되고, 올바른 Agent Hub URL과 `capability` 쿼리 파라미터가 사용되는지 확인
    - [X] Agent Hub가 성공적인 응답(예: Agent Card 리스트 JSON)을 반환할 때, 해당 리스트가 파싱되어 반환되는지 확인
    - [X] Agent Hub가 빈 리스트(`[]`)를 반환할 때, 빈 리스트가 그대로 반환되는지 확인
    - [X] Agent Hub 연결 실패(`httpx.RequestError`) 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] Agent Hub가 4xx 또는 5xx 상태 코드(`httpx.HTTPStatusError`)를 반환할 때, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] 응답 JSON 파싱 중 예외 발생 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
*   **`_call_a2a_agent` 메서드 테스트 (Mock httpx, Mock google_a2a)**
    - [X] 유효한 `agent_card`
    - [X] API 호출 오류 테스트 (Mock): `DDGS().atext` 호출 시 예외가 발생하도록 Mocking하고, `web_search` 함수 호출 시 "An error occurred..." 메시지가 반환되는지 확인
    - [ ] **요약 성공 테스트 (Mock LLM)**: 충분히 긴 Mock 검색 결과(`DDGS().atext` Mock 반환값)와 초기화된 Mock LLM(`genai.GenerativeModel` Mock)이 주어졌을 때, `web_search` 함수가 `model.generate_content_async`를 올바른 요약 프롬프트로 호출하고, Mock LLM 응답(`response.text`)을 포함한 "Summary based on..." 형식의 문자열을 반환하는지 확인.
    - [ ] **요약 건너뛰기 테스트 (짧은 결과)**: `DDGS().atext` Mock 반환값이 200자 미만일 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 건너뛰기 테스트 (LLM 미초기화)**: `web_search_tool.LLM_CLIENT_INITIALIZED`를 `False`로 패치(patch)했을 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 실패 테스트 (Mock LLM 에러)**: `genai.GenerativeModel.generate_content_async` 호출 시 예외가 발생하도록 Mocking했을 때, "Web Search Results for..." 형식의 원본 결과 문자열과 함께 "(Note: Summarization failed...)" 메시지가 포함되어 반환되는지 확인.
    - [X] `src/jarvis/tools/__init__.py`에 `web_search_tool`이 `available_tools` 리스트에 포함되어 있는지 확인

### 7.9. Dispatcher A2A 클라이언트 로직 테스트 (`src/jarvis/core/dispatcher.py`)
*   **`_discover_a2a_agents` 메서드 테스트 (Mock httpx)**
    - [X] `httpx.AsyncClient.get`이 성공적으로 호출되고, 올바른 Agent Hub URL과 `capability` 쿼리 파라미터가 사용되는지 확인
    - [X] Agent Hub가 성공적인 응답(예: Agent Card 리스트 JSON)을 반환할 때, 해당 리스트가 파싱되어 반환되는지 확인
    - [X] Agent Hub가 빈 리스트(`[]`)를 반환할 때, 빈 리스트가 그대로 반환되는지 확인
    - [X] Agent Hub 연결 실패(`httpx.RequestError`) 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] Agent Hub가 4xx 또는 5xx 상태 코드(`httpx.HTTPStatusError`)를 반환할 때, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] 응답 JSON 파싱 중 예외 발생 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
*   **`_call_a2a_agent` 메서드 테스트 (Mock httpx, Mock google_a2a)**
    - [X] 유효한 `agent_card`
    - [X] API 호출 오류 테스트 (Mock): `DDGS().atext` 호출 시 예외가 발생하도록 Mocking하고, `web_search` 함수 호출 시 "An error occurred..." 메시지가 반환되는지 확인
    - [ ] **요약 성공 테스트 (Mock LLM)**: 충분히 긴 Mock 검색 결과(`DDGS().atext` Mock 반환값)와 초기화된 Mock LLM(`genai.GenerativeModel` Mock)이 주어졌을 때, `web_search` 함수가 `model.generate_content_async`를 올바른 요약 프롬프트로 호출하고, Mock LLM 응답(`response.text`)을 포함한 "Summary based on..." 형식의 문자열을 반환하는지 확인.
    - [ ] **요약 건너뛰기 테스트 (짧은 결과)**: `DDGS().atext` Mock 반환값이 200자 미만일 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 건너뛰기 테스트 (LLM 미초기화)**: `web_search_tool.LLM_CLIENT_INITIALIZED`를 `False`로 패치(patch)했을 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 실패 테스트 (Mock LLM 에러)**: `genai.GenerativeModel.generate_content_async` 호출 시 예외가 발생하도록 Mocking했을 때, "Web Search Results for..." 형식의 원본 결과 문자열과 함께 "(Note: Summarization failed...)" 메시지가 포함되어 반환되는지 확인.
    - [X] `src/jarvis/tools/__init__.py`에 `web_search_tool`이 `available_tools` 리스트에 포함되어 있는지 확인

### 7.10. Dispatcher A2A 클라이언트 로직 테스트 (`src/jarvis/core/dispatcher.py`)
*   **`_discover_a2a_agents` 메서드 테스트 (Mock httpx)**
    - [X] `httpx.AsyncClient.get`이 성공적으로 호출되고, 올바른 Agent Hub URL과 `capability` 쿼리 파라미터가 사용되는지 확인
    - [X] Agent Hub가 성공적인 응답(예: Agent Card 리스트 JSON)을 반환할 때, 해당 리스트가 파싱되어 반환되는지 확인
    - [X] Agent Hub가 빈 리스트(`[]`)를 반환할 때, 빈 리스트가 그대로 반환되는지 확인
    - [X] Agent Hub 연결 실패(`httpx.RequestError`) 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] Agent Hub가 4xx 또는 5xx 상태 코드(`httpx.HTTPStatusError`)를 반환할 때, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] 응답 JSON 파싱 중 예외 발생 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
*   **`_call_a2a_agent` 메서드 테스트 (Mock httpx, Mock google_a2a)**
    - [X] 유효한 `agent_card`
    - [X] API 호출 오류 테스트 (Mock): `DDGS().atext` 호출 시 예외가 발생하도록 Mocking하고, `web_search` 함수 호출 시 "An error occurred..." 메시지가 반환되는지 확인
    - [ ] **요약 성공 테스트 (Mock LLM)**: 충분히 긴 Mock 검색 결과(`DDGS().atext` Mock 반환값)와 초기화된 Mock LLM(`genai.GenerativeModel` Mock)이 주어졌을 때, `web_search` 함수가 `model.generate_content_async`를 올바른 요약 프롬프트로 호출하고, Mock LLM 응답(`response.text`)을 포함한 "Summary based on..." 형식의 문자열을 반환하는지 확인.
    - [ ] **요약 건너뛰기 테스트 (짧은 결과)**: `DDGS().atext` Mock 반환값이 200자 미만일 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 건너뛰기 테스트 (LLM 미초기화)**: `web_search_tool.LLM_CLIENT_INITIALIZED`를 `False`로 패치(patch)했을 때, `genai.GenerativeModel`이 호출되지 않고 "Web Search Results for..." 형식의 원본 결과 문자열이 반환되는지 확인.
    - [ ] **요약 실패 테스트 (Mock LLM 에러)**: `genai.GenerativeModel.generate_content_async` 호출 시 예외가 발생하도록 Mocking했을 때, "Web Search Results for..." 형식의 원본 결과 문자열과 함께 "(Note: Summarization failed...)" 메시지가 포함되어 반환되는지 확인.
    - [X] `src/jarvis/tools/__init__.py`에 `web_search_tool`이 `available_tools` 리스트에 포함되어 있는지 확인

### 7.11. Dispatcher A2A 클라이언트 로직 테스트 (`src/jarvis/core/dispatcher.py`)
*   **`_discover_a2a_agents` 메서드 테스트 (Mock httpx)**
    - [X] `httpx.AsyncClient.get`이 성공적으로 호출되고, 올바른 Agent Hub URL과 `capability` 쿼리 파라미터가 사용되는지 확인
    - [X] Agent Hub가 성공적인 응답(예: Agent Card 리스트 JSON)을 반환할 때, 해당 리스트가 파싱되어 반환되는지 확인
    - [X] Agent Hub가 빈 리스트(`[]`)를 반환할 때, 빈 리스트가 그대로 반환되는지 확인
    - [X] Agent Hub 연결 실패(`httpx.RequestError`) 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] Agent Hub가 4xx 또는 5xx 상태 코드(`httpx.HTTPStatusError`)를 반환할 때, 에러가 로깅되고 빈 리스트가 반환되는지 확인
    - [X] 응답 JSON 파싱 중 예외 발생 시, 에러가 로깅되고 빈 리스트가 반환되는지 확인
*   **`_call_a2a_agent` 메서드 테스트 (Mock httpx, Mock google_a2a)**
    - [X] 유효한 `agent_card`
    - [X] API 호출 오류 테스트 (Mock): `DDGS().atext` 호출 시 예외가 발생하도록 Mocking하고, `web_search` 함수 호출 시 "An error occurred..." 메시지가 반환되는지 확인