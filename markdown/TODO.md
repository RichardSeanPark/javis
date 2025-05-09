# 자비스 AI 프레임워크 상세 구현 작업 목록 (TODO.md) - Vibe Coding용

**목표:** `PLAN.md` 기반의 아키텍처와 기능을 AI 어시스턴트가 단계별로 구현할 수 있도록 매우 상세하게 기술한 작업 목록입니다. 체크리스트를 통해 진행 상황을 추적합니다.

## 0. 프로젝트 초기 설정

- [X] **Poetry 초기화**: 터미널에서 `poetry init` 명령어를 실행하여 프로젝트 설정을 시작하고 `pyproject.toml` 파일을 생성합니다. 대화형 프롬프트에 따라 프로젝트 이름, 버전, 설명 등을 입력합니다.
- [X] **Git repository 생성**: 터미널에서 github에 repository를 생성합니다.
- [X] **기본 디렉토리 생성**: 터미널에서 `mkdir src tests docs scripts data diagrams markdown config` 명령어를 실행하여 표준 프로젝트 구조를 만듭니다.
- [X] **초기 의존성 추가** (`pyproject.toml` 직접 수정 또는 `poetry add <package_name>` 명령어 사용):
    - [X] `google-adk`: Google Agent Development Kit 프레임워크 핵심 라이브러리를 추가합니다.
    - [X] `google-cloud-aiplatform`: Vertex AI 서비스(Gemini, Codey 모델 등)에 접근하기 위한 라이브러리를 추가합니다.
    - [X] `python-dotenv`: `.env` 파일에서 환경 변수를 로드하기 위한 라이브러리를 추가합니다.
    - [X] `fastapi`: (커스텀 웹 UI 선택 시) API 서버 구축을 위한 웹 프레임워크를 추가합니다.
    - [X] `uvicorn[standard]`: (커스텀 웹 UI 선택 시) FastAPI 애플리케이션을 실행하기 위한 ASGI 서버를 추가합니다.
    - [X] `pydantic`: 데이터 유효성 검사 및 설정을 위한 모델 정의 라이브러리를 추가합니다.
- [X] **`.gitignore` 파일 생성**: 루트 디렉토리에 `.gitignore` 파일을 생성하고, Python 가상 환경, 컴파일된 파일, IDE 설정 파일, OS 특정 파일, 그리고 중요한 `.env` 파일 등을 Git 추적에서 제외하도록 관련 패턴을 추가합니다. (예: `__pycache__/`, `*.pyc`, `.env`, `.idea/`, `.vscode/`, `*.DS_Store`)
- [X] **`README.md` 초기 파일 생성**: 루트 디렉토리에 `README.md` 파일을 생성하고 최소한 프로젝트 제목이라도 작성합니다.
- [X] **`.env.example` 파일 생성**: 루트 디렉토리에 `.env.example` 파일을 생성합니다. 이 파일에는 프로젝트 실행에 필요한 환경 변수들의 이름만 목록으로 정의하고, 실제 값은 비워둡니다. 예를 들어 `GEMINI_API_KEY=` 와 `GCP_PROJECT_ID=` 같이 줄을 추가합니다.
- [X] **`.env` 파일 생성**: `.env.example` 파일을 복사하여 `.env` 파일을 생성합니다. 이 파일에 실제 API 키, Google Cloud 프로젝트 ID 등 민감한 설정 값을 입력합니다. 이 파일은 반드시 `.gitignore`에 추가하여 Git 저장소에 포함되지 않도록 합니다.
- [X] **기본 `src` 구조 생성**: `src/jarvis/` 디렉토리 내에 빈 `__init__.py` 파일을 생성하여 `jarvis`를 Python 패키지로 만듭니다. 하위 디렉토리(`core`, `components`, `agents`, `tools`, `interfaces`, `models`) 생성.

## 1. 사용자 인터페이스 계층 (선택적 초기 구현)

*   **1.1. CLI 인터페이스 (ADK 활용)**
    - [X] **파일 생성**: `src/jarvis/__init__.py` 파일 수정하여 최소한의 `root_agent` 임포트 준비
    - [X] **임시 에이전트 정의**: `src/jarvis/core/dispatcher.py` 파일 생성 및 임시 `root_agent` 정의 (ADK `Agent` 사용, 간단한 `name`, `description` 설정)
        - 이 파일에서는 `google.adk` 모듈에서 `Agent` 클래스를 가져옵니다.
        - `root_agent` 변수를 생성하여 `Agent` 클래스의 인스턴스를 할당합니다.
        - 해당 에이전트에 "JarvisDispatcherPlaceholder"라는 이름과 "Jarvis AI Framework Root Agent (Placeholder)"라는 설명을 부여합니다.
    - [X] **패키지 노출**: `src/jarvis/__init__.py` 파일에 `from .core.dispatcher import root_agent` 추가
    - [X] **실행 테스트**: 프로젝트 루트에서 `adk run .` 실행하여 "JarvisDispatcherPlaceholder" 에이전트가 로드되고 프롬프트가 나타나는지 확인

*   **1.2. 웹 UI (ADK Web 활용)**
    - [X] **(선행 작업)** 1.1의 임시 에이전트 정의 완료 필요
    - [X] **실행 테스트**: 프로젝트 루트에서 `adk web .` 실행
    - [X] **웹 접속 확인**: 브라우저에서 `http://localhost:8000` (또는 터미널에 표시된 주소) 접속하여 ADK Web UI가 로드되고 "JarvisDispatcherPlaceholder" 에이전트를 선택할 수 있는지 확인

*   **1.3. (선택사항) 커스텀 웹 UI (FastAPI + React)**
    - [X] **FastAPI 앱 생성**: `src/jarvis/interfaces/api/main.py` 파일 생성
        - 이 파일에서는 `fastapi` 모듈에서 `FastAPI` 클래스를 가져옵니다.
        - `FastAPI` 클래스의 인스턴스를 생성하여 `app` 변수에 할당하고, 제목은 "Jarvis API"로 설정합니다.
        - 루트 경로('/')에 대한 GET 요청 핸들러 함수 `read_root()`를 정의합니다. 이 함수는 "Welcome to Jarvis API" 메시지를 포함한 JSON 응답을 반환합니다.
        - 향후 '/chat' 엔드포인트를 추가할 예정임을 주석으로 표시합니다.
    - [X] **실행 스크립트 추가** (`pyproject.toml`의 `[tool.poetry.scripts]` 또는 별도 `run_api.py`)
    - [X] **API 서버 실행 테스트**: `uvicorn src.jarvis.interfaces.api.main:app --reload` 명령어로 서버 실행 확인
    - [-] **(후속 작업)** `/chat` 엔드포인트 구현 및 프론트엔드 개발은 별도 계획

## 2. 입력 처리 및 파싱 계층 (`src/jarvis/components/input_parser.py`)

- [X] **2.1. 데이터 모델 정의 (`src/jarvis/models/input.py`)**
    - [X] `src/jarvis/models/` 디렉토리에 `input.py` 파일을 생성합니다. Pydantic의 `BaseModel`을 사용하여 입력 처리 결과를 담을 `ParsedInput` 데이터 클래스를 정의합니다. 이 클래스는 입력 파서의 최종 출력 구조를 나타냅니다.
    - [X] `ParsedInput` 클래스에는 다음과 같은 필드를 포함시킵니다:
        *   `original_text`: 사용자가 입력한 원본 텍스트 (문자열 타입, `str`).
        *   `original_language`: 감지된 원본 텍스트의 언어 코드 (문자열 타입, `str`, 예: 'ko', 'en'). Pydantic의 `Field`를 사용하여 필수 필드임을 명시하고 설명을 추가할 수 있습니다.
        *   `english_text`: 원본 텍스트를 영어로 번역한 결과 (문자열 타입, `str`). 이 또한 필수 필드로 지정합니다.
        *   `intent`: 분석된 사용자의 주된 의도 (선택적 문자열 타입, `Optional[str]`, 예: 'code_generation', 'question_answering').
        *   `entities`: 텍스트에서 추출된 주요 엔티티 정보 (선택적 딕셔너리 타입, `Optional[Dict[str, Any]]`).
        *   `domain`: 식별된 요청의 주 도메인 (선택적 문자열 타입, `Optional[str]`, 예: 'coding', 'general').
        *   필요에 따라 다른 관련 필드(예: 신뢰도 점수)를 추가할 수 있습니다.
- [X] **2.2. `InputParserAgent` 클래스 정의 (`src/jarvis/components/input_parser.py`)**
    - [X] ADK `LlmAgent` 상속 (`google.adk.agents` 사용)
        - [X] 이 파일에서는 `google.adk.agents` 모듈에서 `LlmAgent` 클래스를 가져옵니다.
        - [X] `src.jarvis.models.input` 모듈에서 `ParsedInput` 클래스를 가져옵니다.
        - [X] 필요시 Google Cloud와 Vertex AI 서비스를 위한 라이브러리를 가져옵니다.
        - [X] `InputParserAgent` 클래스를 정의하고 `LlmAgent`를 상속받습니다.
    - [X] `__init__` 메서드 구현
        - 부모 클래스(`LlmAgent`) 초기화 시 `name`, `description`, `model` 파라미터 전달 (예: `model="gemini-2.0-flash-exp"`).
        - 필요시 추가적인 모델 초기화 코드를 구현할 수 있습니다.
    - [X] `process_input` 메서드 정의
        - 사용자 입력(`user_input`)을 받아 `ParsedInput` 객체를 반환하는 비동기 함수(`async def`)로 구현합니다.
        - 이 메서드의 상세 구현(언어 감지, 번역 등)은 다음 단계에서 진행됩니다.
- [X] **2.3. 언어 감지 기능 구현 (`process_input` 메서드 내)**
    - [X] `google.generativeai` 클라이언트를 사용하여 LLM 호출 로직 작성 (`model.generate_content_async`)
    - [X] 언어 감지용 프롬프트 설계 (ISO 639-1 코드만 반환하도록 요청)
    - [X] LLM 응답에서 정규식 등을 사용하여 언어 코드 추출 및 `original_language` 변수에 저장 (오류 처리 포함)
- [X] **2.4. 영어 번역 기능 구현 (`process_input` 메서드 내)**
    - [X] `original_language`가 'en'이 아닌 경우에만 실행
    - [X] LLM 호출 로직 작성
    - [X] 영어 번역용 프롬프트 설계 (예: `"Translate the following text from {original_language} to English:\\n\\nText: {user_input}"`)
    - [X] LLM 응답에서 번역된 텍스트 추출 및 `english_text` 변수에 저장 (원본이 영어면 `user_input` 그대로 저장)
- [X] **2.5. 의도/엔티티/도메인 분석 기능 구현 (`process_input` 메서드 내)**
    - [X] LLM 호출 로직 작성 (입력은 `english_text` 사용, 내부 처리는 항상 영어로 진행)
    - [X] 분석용 프롬프트 설계 (예: `"Analyze the following English text. Identify the primary intent (e.g., code_generation, question_answering, document_summary), extract key entities (as JSON if possible), and determine the main domain (e.g., coding, finance, general). Text: {english_text}"`)
    - [X] LLM 응답 파싱하여 `intent`, `entities`, `domain` 추출 및 변수에 저장
- [X] **2.6. `ParsedInput` 객체 생성 및 반환 (`process_input` 메서드 내)**
    - [X] 수집된 정보 (`original_text`, `original_language`, `english_text`, `intent`, `entities`, `domain`)를 사용하여 `ParsedInput` 객체 인스턴스화
    - [X] 생성된 `ParsedInput` 객체 반환
- [X] **2.7. 모듈 등록 (`src/jarvis/components/__init__.py`)**
    - [X] `from .input_parser import InputParserAgent` 추가 (및 관련 통합 테스트)

## 3. 에이전트 라우팅 계층 (MCP/Dispatcher) (`src/jarvis/core/dispatcher.py`)

- [X] **3.1. `JarvisDispatcher` 클래스 정의**
    - [X] 기존 임시 `root_agent`를 `JarvisDispatcher` 클래스로 변경 (ADK `LlmAgent` 상속)
    - [X] `__init__` 메서드 정의:
        *   `name="JarvisDispatcher"`, `description="Central dispatcher for the Jarvis AI Framework. Analyzes requests and routes them to the appropriate specialized agent."` 설정
        *   `model="gemini-2.0-flash-exp"` 설정 (라우팅 결정 및 자동 위임용 모델, `LlmConfig` 대신 직접 전달)
        *   `InputParserAgent` 인스턴스 생성 및 멤버 변수로 저장 (`self.input_parser = InputParserAgent()`)
        *   하위 도메인 에이전트들을 저장할 딕셔너리 또는 리스트 초기화 (`self.sub_agents = {}`)
        *   (나중에 추가) Agent Hub 클라이언트 초기화
- [X] **3.2. 하위 에이전트 등록 메서드 구현 (`register_agent`)**: 하위 에이전트 인스턴스를 `self.sub_agents` 또는 `self.sub_agents_list`에 추가하는 로직
- [X] **3.3. 메인 처리 로직 구현 (`__call__` 또는 `process_request` 메서드)**
    - [X] 사용자 입력 문자열을 인자로 받음
    - [X] `self.input_parser.process_input()` 호출하여 `ParsedInput` 객체 얻기
    - [X] `ParsedInput` 객체와 `original_language` 정보 저장
    - [X] **라우팅 결정 로직 시작 (단계적 구현)**
        - [X] **3.3.1. 규칙 기반 라우팅 구현**: `ParsedInput.intent` 또는 `ParsedInput.domain` 기반으로 특정 키를 가진 `self.sub_agents`를 직접 선택하는 조건문 추가 (초기 단계)
        - [X] **3.3.2. ADK 자동 위임 설정**: \
            * `JarvisDispatcher`의 `tools` 속성에 하위 에이전트들을 추가 (또는 `sub_agents` 파라미터 활용)\n            * LLM이 각 에이전트의 `description`을 기반으로 작업을 자동으로 적합한 하위 에이전트에 위임하도록 설정\n            * 디스패처의 `instruction`에 라우팅 가이드라인 추가 (예: "Route the user's request based on the following specialized agents: ...")
            * ADK의 자동 위임 기능을 활용하여 LLM이 자연스럽게 적합한 하위 에이전트를 선택하도록 함 (Live API 테스트 포함)
         - [X] **3.3.3. A2A 동적 검색 로직 구현**: (Dispatcher 관점의 검색/호출 로직 구현 완료, Mock 테스트 통과)
             *   [X] 내부 에이전트로 처리 불가 시 `_discover_a2a_agents` 호출하여 Agent Hub에 검색 요청
             *   [X] Discovery 쿼리에 필요한 능력(capability) 전달
             *   [X] 검색된 A2A 에이전트 목록에서 첫 번째 에이전트 선택 (선택 로직 상세화는 TODO)
             *   [X] 선택된 에이전트에 대해 `_call_a2a_agent` 호출하여 A2A 통신 수행 및 결과 반환
- [X] **3.4. 선택된 에이전트 호출 및 컨텍스트/툴 주입**
    - [X] Dispatcher가 위임 결정 시 필요한 정보(`DelegationInfo`: 에이전트 이름, 입력, 언어, 툴, 대화 이력)를 반환하도록 수정
    - [X] Runner로부터 `_run_async_impl` 호출 시, `DelegationInfo`를 기반으로:
        - [X] 위임 대상 에이전트에게 필요한 툴 목록(`DelegationInfo.required_tools`)을 임시로 설정
        - [X] 위임 대상 에이전트의 `instruction`에 컨텍스트 정보(대화 이력, 원본 언어)를 임시로 추가
        - [X] 실행 후 원래 `tools`와 `instruction`으로 복구
        - [X] Runner가 실제 호출을 수행하도록 위임 `Event` 반환 (실제 호출 로직은 Runner 담당)
- [X] **3.5. 결과 처리 및 반환**
    - [X] 하위 에이전트로부터 **영어 결과** 수신
    - [X] 최종 응답 생성기로 전달 (또는 Dispatcher가 직접 처리 - 6단계에서 상세화)
    - [X] (툴 구현은 5단계에서) 웹 검색 툴 인터페이스 정의 (`web_search` 함수 시그니처)
    - [X] (툴 구현은 5단계에서) 번역 툴 인터페이스 정의 (`translate_text` 함수 시그니처)
- [X] **3.6. 에러 핸들링**: 입력 파싱 실패, 라우팅 실패, 하위 에이전트 실행 오류 등에 대한 예외 처리 로직 추가
- [X] **3.7. 패키지 루트 노출**: `src/jarvis/__init__.py` 에서 `root_agent = JarvisDispatcher()` 인스턴스 생성 및 노출

## 4. 도메인별 에이전트 모듈 계층 (초기 에이전트 2개 구현)

*   **4.1. 코딩 에이전트 (`src/jarvis/agents/coding_agent.py`)**
    - [X] `CodingAgent` 클래스 정의 (ADK `LlmAgent` 상속)
    - [X] `__init__` 메서드: `name="CodingAgent"`, `description="Generates, analyzes, debugs, and optimizes code based on user requests in English."`, `model` 설정. 필요한 툴(코드 실행기 등) 등록 placeholder.
    - [X] `instruction` 필드: 에이전트의 역할, 작동 방식, 출력 형식 등을 영어로 상세히 기술
    - [X] (툴 구현은 5단계에서) 코드 실행기 툴 인터페이스 정의 (`execute_python_code` 함수 시그니처)
    - [X] 모듈 등록: `src/jarvis/agents/__init__.py` 생성 및 `from .coding_agent import CodingAgent` 추가
*   **4.2. 지식 QA 에이전트 (`src/jarvis/agents/qa_agent.py`)**
    - [X] `KnowledgeQA_Agent` 클래스 정의 (ADK `LlmAgent` 상속)
    - [X] `__init__` 메서드: `name="KnowledgeQA_Agent"`, `description="Answers general knowledge questions in English. Can use web search for up-to-date information."`, `model` 설정. 웹 검색 툴 등록 placeholder.
    - [X] `instruction` 필드: 역할, 웹 검색 사용 시점, 답변 형식 등을 영어로 기술
    - [X] (툴 구현은 5단계에서) 웹 검색 툴 인터페이스 정의 (`web_search` 함수 시그니처)
    - [X] (툴 구현은 5단계에서) 번역 툴 인터페이스 정의 (`translate_text` 함수 시그니처)
    - [X] 모듈 등록: `src/jarvis/agents/__init__.py`에 `from .qa_agent import KnowledgeQA_Agent` 추가
*   **4.3. Dispatcher에 초기 에이전트 등록**
    - [X] `src/jarvis/core/dispatcher.py` 수정:
        *   [X] `CodingAgent`와 `KnowledgeQA_Agent` 임포트
        *   [X] `JarvisDispatcher.__init__` 내에서 두 에이전트 인스턴스 생성
        *   [X] `register_agent` 메서드 호출 또는 `sub_agents` 리스트/딕셔너리에 추가
        *   [X] Dispatcher의 `tools` 속성 또는 `sub_agents` 파라미터에 이 에이전트들을 포함시켜 자동 위임 준비

## 5. [X] 툴 및 컨텍스트 관리 계층

*   **5.1. 툴 정의 (`src/jarvis/tools/`)**
    - [X] **번역 툴 (`src/jarvis/tools/translate_tool.py`)**
        - [X] `translate_text(text: str, target_language: str, source_language: str = 'auto') -> str` 함수 정의
        - [X] 함수 내부에 LLM 호출 로직 구현 (번역용 프롬프트 사용, 예: `"Translate the following text from {source_language} to {target_language}: {text}"`)
        - [X] ADK `Tool` 객체 생성 (`function_declarations`에 함수 정보 명시, `description` 포함)
        - [X] `source_language`와 `target_language` 파라미터는 ISO 639-1 언어 코드 사용 (예: 'ko', 'en', 'ja')
    - [X] **웹 검색 툴 (`src/jarvis/tools/web_search_tool.py`)**
        - [X] `web_search(query: str) -> str` 함수 정의
        - [X] 외부 검색 API (예: Google Custom Search API, Tavily API 등) 호출 로직 구현 (duckduckgo_search 사용)
        - [X] 검색 결과 요약 또는 가공 로직 (필요시 LLM 추가 호출) # <<< Mark as completed
        - [X] ADK `Tool` 객체 생성 (`description` 자동 설정됨)
    - [X] **코드 실행 툴 (`src/jarvis/tools/code_execution_tool.py`)**
        - [X] `execute_python_code(code: str) -> str` 함수 정의
        - [X] 보안 중요: 코드를 안전한 샌드박스 환경(RestrictedPython 사용)에서 실행하는 로직 구현 # <<< Update status and comment
        - [X] 실행 결과(stdout, stderr) 캡처 및 반환 로직 (stdout은 제한됨)
        - [X] ADK `Tool` 객체 생성 (`description` 자동 설정됨)
    - [X] **툴 모듈 등록 (`src/jarvis/tools/__init__.py`)**: 생성된 `Tool` 객체들 임포트 및 리스트로 관리 (예: `available_tools = [translate_tool, web_search_tool, code_execution_tool]`)
*   **5.2. 툴 레지스트리 및 주입 로직 (`src/jarvis/core/dispatcher.py`)**
    - [X] `src/jarvis/tools` 에서 `available_tools` 임포트
    - [X] Dispatcher가 하위 에이전트 호출 시, 해당 에이전트에 필요한 툴만 전달하는 로직 설계 (agent_tool_map 정의)
    - [X] (향후 구현) 실제 툴 주입 로직 구현
*   **5.3. 컨텍스트 관리 (`src/jarvis/core/context_manager.py`)**
    - [X] **클래스 정의**: `ContextManager` 클래스 생성
    - [X] **대화 이력 관리**: 세션 ID별 대화 이력(사용자 입력, AI 응답, 원본 언어) 저장 및 검색 메서드 구현 (간단한 딕셔너리 또는 Redis 등 활용)
    - [X] **컨텍스트 제공**: 특정 세션 ID에 대한 컨텍스트(최근 N개 대화, 원본 언어 등)를 포맷하여 반환하는 메서드 구현
    - [X] **Dispatcher 연동**: Dispatcher에서 `ContextManager` 인스턴스 사용. 에이전트 호출 전 필요한 컨텍스트 검색 및 전달 로직 추가.

## 6. 응답 생성 및 출력 계층 (`src/jarvis/components/response_generator.py`)

- [X] **6.1. `ResponseGenerator` 클래스 정의**
    - [X] (간단한 경우) 일반 Python 클래스 또는 (복잡한 경우) ADK `Agent`로 정의 가능
    - [X] `__init__` 메서드: 번역 툴 인스턴스화 (또는 외부에서 주입받기)
    - [X] `generate_response(english_result: Any, original_language: str) -> str` 메서드 정의
- [X] **6.2. 결과 처리 및 포맷팅 (`generate_response` 메서드 내)**
    - [X] 입력받은 `english_result` (텍스트, JSON 등)를 사용자 친화적 텍스트로 변환/요약 (필요시 LLM 추가 호출) # 기본 포맷팅만 구현
- [X] **6.3. 최종 응답 번역 (`generate_response` 메서드 내)**
    - [X] `original_language`가 'en'이 아닌 경우, 포맷팅된 영어 응답 텍스트를 `original_language`로 번역 (번역 툴 호출)
    - [X] 번역 시 ISO 639-1 언어 코드 사용 (예: 'ko', 'en', 'ja')
    - [X] 번역된 텍스트 또는 원본 영어 텍스트를 최종 반환값으로 설정
- [X] **6.4. Dispatcher 연동**: `src/jarvis/core/dispatcher.py` 에서 `ResponseGenerator` 사용
    - [X] 하위 에이전트로부터 결과 수신 후, `ResponseGenerator.generate_response()` 호출 (영어 결과와 원본 언어 전달)
    - [X] 최종 번역된 응답을 사용자 인터페이스로 반환
- [X] **6.5. 모듈 등록 (`src/jarvis/components/__init__.py`)**: `from .response_generator import ResponseGenerator` 추가

## 7. 에이전트 간 상호작용 (A2A 연동 - 심화 단계)

- [X] **7.1. Agent Hub 서버 구현 (`src/jarvis/interfaces/agent_hub/server.py`)**
    - [X] FastAPI 또는 Flask 기반으로 A2A Discovery API 엔드포인트 (`/discover`) 구현
    - [X] 에이전트 등록/관리 기능 구현 (인메모리 딕셔너리 또는 간단한 DB 사용)
    - [X] Agent Card 저장 및 검색 로직 구현
- [X] **7.2. A2A 통신 라이브러리 설정**: `google-a2a-python` 라이브러리 설치 및 기본 설정
- [X] **7.3. ADK 에이전트 A2A 노출**: 각 ADK 에이전트(예: `CodingAgent`)를 A2A 프로토콜로 호출 가능하도록 A2A 서버 래퍼 구현 (라이브러리 활용)
- [X] **7.4. Dispatcher A2A 클라이언트 로직**: 
    - [X] Agent Hub `/discover` API 호출 및 검색된 A2A 에이전트(자체 ADK 에이전트 포함)와 통신하는 로직 구현
    - [X] A2A Discovery 쿼리 구조화 (능력 기술, 필요한 입출력 형식 등 명시)
    - [X] A2A 응답 처리 및 에이전트 선택 로직 구현
- [X] **7.5. Agent Card 정의 (`config/agent_cards/`)**: 
    - [X] 각 에이전트(Coding, QA)의 능력을 상세히 기술한 JSON 파일 생성
    - [X] Agent Card에는 에이전트 이름, 설명, 지원하는 능력 목록, 입출력 형식, 인증 요구사항 등을 명시
- [X] **7.6. A2A Task 표준 적용**: 
    - [X] 작업 요청/응답 시 `google-a2a-python` 라이브러리의 Task 관련 클래스 사용 (`common.types` 활용)
    - [X] `Task`, `TaskStatus`, `TaskState` 등 A2A 표준 클래스를 활용하여 작업 생성 및 관리 (`_call_a2a_agent` 구현 확인)
    - [X] 작업 상태 추적 및 결과 처리 로직 구현 (`_call_a2a_agent` 구현 확인)

---
**참고:** 이 목록은 Vibe Coding을 위한 매우 상세한 가이드이며, 실제 구현 중 AI 어시스턴트와의 상호작용을 통해 각 단계를 진행하고 확인합니다. 필요에 따라 목록은 수정될 수 있습니다. 