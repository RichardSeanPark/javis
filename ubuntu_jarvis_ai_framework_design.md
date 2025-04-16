# Ubuntu 기반 Jarvis 스타일 AI 에이전트 프레임워크 설계

## 1. 개요

Ubuntu 리눅스 환경에서 동작하며 웹 서비스로도 제공 가능한 Jarvis 스타일 AI 프레임워크를 설계합니다. 이 프레임워크는 사용자의 다양한 입력(자연어, 이미지, 음성, 동영상 등)을 받아, 요청의 성격에 따라 자동으로 적합한 에이전트(agent)를 호출하여 처리하는 것을 목표로 합니다.

**주요 목표:**

*   어떠한 종류의 질문(코딩, 문서 작성, 문화, 데이터 분석 등)에도 각 도메인에 특화된 에이전트가 대응합니다.
*   전체 시스템은 다중 에이전트를 가장 효율적으로 **오케스트레이션(조율)**하도록 구성됩니다.
*   **Google Agent Development Kit (ADK)**와 Agent2Agent (A2A) 프레임워크만을 활용하여 구현합니다.
*   유사 기능의 에이전트들을 모듈화하고 중앙 관리 컴포넌트(MCP 또는 Dispatcher)를 통해 라우팅 및 제어합니다.

본 문서에서는 제안하는 전체 아키텍처 개념, 핵심 구성 요소의 역할, Google ADK/A2A의 활용 방식, 예시 시나리오, 성능 최적화 전략, 보안 고려 사항을 상세히 설명합니다.

## 2. 전체 아키텍처 개요

제안하는 Jarvis 스타일 AI 프레임워크의 아키텍처는 **다계층 에이전트 시스템**으로 구성됩니다.

```mermaid
graph TD
    A[사용자 인터페이스 계층] --> B(입력 처리 및 파싱 계층);
    B --> C{에이전트 라우팅 계층 (MCP/Dispatcher)};
    C --> D[도메인별 에이전트 모듈 계층];
    D --> E(툴 및 컨텍스트 관리 계층);
    D --> F[응답 생성 및 출력 계층];
    E --> D;
    F --> A;
```

![Jarvis AI Framework Architecture Diagram](diagrams/new_architecture_diagram.png)

**각 계층의 역할:**

1.  **사용자 인터페이스 계층:**
    *   웹 UI, CLI, API 등의 형태로 사용자 입력을 받고 응답을 반환합니다. (예: 웹 브라우저 채팅 인터페이스, 터미널 CLI 등)
    *   ADK는 다양한 인터페이스(CLI, 웹 UI, API 서버, Python API)를 지원하여 Ubuntu 서버와 웹 클라이언트를 모두 수용 가능합니다. ([출처: Google Developers Blog](https://developers.googleblog.com))

2.  **입력 처리 및 파싱 계층:**
    *   사용자의 멀티모달 입력을 전처리하고 이해합니다. (텍스트 분류, 음성 STT, 이미지 OCR/비전 분석 등)
    *   입력의 **의도(intent)**, 요청 유형, 도메인을 식별합니다.
    *   ADK는 멀티모달 인터랙션을 지원하여 입력 처리 모듈 통합이 용이합니다. ([출처: Google Developers Blog](https://developers.googleblog.com))

3.  **에이전트 라우팅 계층 (MCP/Dispatcher):**
    *   중앙 관리자/디스패처 컴포넌트로, 입력 분석 결과를 기반으로 처리할 에이전트 또는 에이전트 조합을 결정하고 전체 워크플로우를 조율합니다.
    *   **하이브리드 라우팅 전략**: Google ADK의 계층 구조와 자동 위임 기능을 활용한 **내부 라우팅**과, 필요시 Agent Hub 및 A2A 프로토콜을 통한 **외부/동적 라우팅**을 결합하여 사용합니다.
    *   규칙 기반, 설명 기반 위임(ADK), 능력 기반 검색(A2A) 등 다양한 라우팅 메커니즘을 활용합니다.
    *   Anthropic의 MCP 개념처럼 **맥락(Context)**과 **도구(tool)**를 적절한 에이전트에 공급하고 라우팅을 총괄합니다.

4.  **도메인별 에이전트 모듈 계층:**
    *   실제 작업을 수행하는 전문 에이전트들의 집합입니다. 각 에이전트는 특정 도메인/기능에 특화됩니다.
    *   **예시 에이전트:**
        *   **코딩 에이전트:** 코드 생성/디버깅 (Codey, Codex 등 활용)
        *   **문서 작성 에이전트:** 보고서/요약 작성 (GPT 계열 LLM 활용)
        *   **지식 QA 에이전트:** 일반 질문 답변 (대형 LLM, 웹 검색 활용)
        *   **이미지 분석 에이전트:** 이미지 내용 묘사/분석 (비전 모델, OCR 활용)
        *   **데이터 분석 에이전트:** 통계 분석, 시각화 (pandas, 그래프 생성 도구 활용)
    *   각 에이전트는 모듈화되어 독립적 개발/업데이트가 가능하며, Google ADK의 `LlmAgent`/`Agent` 클래스로 쉽게 구현됩니다. ([출처: Google Developers Blog](https://developers.googleblog.com), [ADK 문서](https://developers.googleblog.com))
    *   ADK는 계층적 관계 설정 및 **설명서(description)** 기반 위임을 지원합니다. ([출처: Google Developers Blog](https://developers.googleblog.com), [ADK 문서](https://developers.googleblog.com))

5.  **툴 및 컨텍스트 관리 계층:**
    *   에이전트들이 사용할 수 있는 외부 도구 모음(Tool Registry)과 공유 컨텍스트를 관리합니다. (코드 실행기, 웹 검색기, 번역기 등)
    *   ADK는 에이전트 내 툴 호출 오케스트레이션을 지원합니다. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   에이전트별 도구 사용 권한을 관리합니다.
    *   공용 컨텍스트 저장소(과거 대화, 세션 상태 등) 역할을 수행합니다.
    *   A2A 프로토콜의 Capability Discovery (Agent Card)와 Collaboration 개념을 적용하여 도구/지식/에이전트를 검색하고 활용합니다. ([출처: Google Developers Blog](https://developers.googleblog.com), [A2A 문서](https://developers.googleblog.com))

6.  **응답 생성 및 출력 계층:**
    *   에이전트들의 처리 결과를 취합하여 최종 사용자 응답을 생성합니다.
    *   결과 병합, 정리, 포맷팅 작업을 수행합니다.
    *   A2A 프로토콜의 User Experience Negotiation 기능을 적용하여 출력 형식을 조율합니다. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   사용자에게 적합한 형태(텍스트, 표, 그래프 등)로 출력합니다.

**데이터 흐름:**

사용자 질의 → 입력 파서 분석 → Dispatcher 라우팅 → 에이전트 처리 (도구/컨텍스트 활용) → 응답 생성 → 사용자 반환

![Jarvis AI Framework Data Flow Diagram](diagrams/new_data_flow_diagram.png)

## 3. 핵심 컴포넌트별 상세 설명

### 3.1. 입력 파서 및 모달리티 처리

*   **역할:** 사용자 입력을 해석하여 요청 유형, 모달리티, 필요 작업을 추론합니다.
*   **처리:**
    *   **텍스트:** 의도 분류, 내용 요약, 질문/명령 판단
    *   **음성:** STT 엔진으로 텍스트 변환
    *   **이미지/동영상:** 비전 분석(객체 인식, OCR), 임베딩 생성
*   **ADK 활용:**
    *   Google Cloud Vertex AI Model Garden의 다양한 모델(Gemini 등 멀티모달 LLM) 통합 가능. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   모달 처리 엔진을 에이전트로 래핑하여 파이프라인에 포함.
*   **컨텍스트 파악:** 이전 대화 내용을 파악하여 MCP적 맥락 관리 기능 제공.

### 3.2. Dispatcher (MCP 역할의 관리자)

*   **역할:** 시스템 내 요청 라우팅 및 오케스트레이션 담당. 입력 파서 결과 기반으로 작업 에이전트 할당.
*   **라우팅 실행:**
    *   **ADK 내부 위임:** Google ADK의 자동 위임 기능 등을 활용하여 내부 에이전트에게 효과적으로 작업 전달.
    *   **규칙 기반 직접 호출:** 명확한 규칙에 따라 특정 에이전트 직접 호출.
    *   **A2A 검색 요청**: 필요시 Agent Hub에 A2A Discovery 요청하여 외부/이기종 에이전트 검색 및 통신 시작.
*   **오케스트레이션**: ADK 및 A2A 기반 에이전트가 혼합된 복잡한 워크플로우 조율.
*   **기타 기능:**
    *   흐름 제어, 에러 핸들링, 로드 밸런싱.
    *   공통 툴박스 및 컨텍스트 주입.
    *   에이전트 인증/인가 (A2A 프로토콜 연계 가능).
*   **구현:** Google ADK 프레임워크를 기반으로 구현 (예: 최상위 LlmAgent).

### 3.3. 에이전트 허브 및 모듈 (Agent Hub & Modules)

*   **역할:** 에이전트 레지스트리, 관리 및 A2A Discovery 서비스 제공.
*   **관리:**
    *   에이전트 모듈 초기화 및 허브 등록 (ADK 및 외부 A2A 에이전트).
    *   에이전트 메타데이터 관리 (Agent Card 포함).
*   **A2A Discovery 서비스:** Agent Card 기반 능력 검색 요청 처리 및 결과 반환.
*   **모니터링:** 에이전트 상태, 성능, 리소스 사용량 추적 및 Task Management 지원.

### 3.4. 툴 레지스트리와 자동 컨텍스트 라우팅

*   **툴 레지스트리:**
    *   **역할:** 에이전트가 사용할 외부 API, 함수, 리소스 관리.
    *   **ADK 활용:** Python 함수를 툴로 정의, Docstring으로 사용법 기술하여 LLM 자동 호출 지원. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   툴별 사용 권한 지정.
    *   Dispatcher가 에이전트에게 허용된 툴 목록 전달/주입. ([출처: Google Developers Blog](https://developers.googleblog.com), [ADK 문서](https://developers.googleblog.com))
*   **자동 컨텍스트 라우팅:**
    *   **역할:** 요청 관련 추가 컨텍스트(배경지식, 이전 대화, 유저 프로필 등)를 해당 에이전트에게 자동 전달.
    *   **구현:** 세션 메모리, 벡터 DB 활용.
    *   Anthropic MCP (프롬프트 컨텍스트 주입) 및 A2A 프로토콜 (메시지 내 컨텍스트 필드) 연계 가능. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   A2A 메시지의 **콘텐츠 타입 파트(parts)** 활용하여 멀티모달 컨텍스트 전달. ([출처: Google Developers Blog](https://developers.googleblog.com))
*   **장점:** 시스템 지능 및 사용자 경험 향상, 에이전트 책임 분리 명확화.

## 4. Google ADK와 A2A의 역할 및 사용 방식

![Component Hierarchy Diagram](diagrams/component_hierarchy_diagram.png)

### 4.1. Google Agent Development Kit (ADK)의 역할

Google ADK는 이 설계의 중심 축을 이루는 오픈소스 에이전트 개발 프레임워크입니다.

*   **에이전트 구현 간소화:**
    *   Python toolkit으로 핵심 로직(프롬프트, 모델, 툴) 작성 용이. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   `Agent`/`LlmAgent` 클래스로 에이전트 정의, ADK 런타임이 나머지 처리. ([출처: Google Developers Blog](https://developers.googleblog.com))
*   **다중 에이전트/서브에이전트 구조 지원:**
    *   계층적 구조 및 에이전트 간 위임 메커니즘 제공. ([출처: Google Developers Blog](https://developers.googleblog.com), [ADK 문서](https://developers.googleblog.com))
    *   설명 기반(**description-driven**) 라우팅 및 **자동 위임(auto delegation)** 활용. ([출처: Google Developers Blog](https://developers.googleblog.com))
*   **툴 통합과 상태 관리:**
    *   에이전트 내 툴 호출 오케스트레이션 및 세션 상태 저장 기능 내장. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   Docstring과 instruction 중심으로 툴 사용 로직 구현.
*   **멀티모달 및 스트리밍 지원:**
    *   양방향 스트리밍으로 오디오/비디오 등 실시간 인터랙션 구현 가능. ([출처: Google Developers Blog](https://developers.googleblog.com))
*   **배포 및 인터페이스:**
    *   다양한 인터페이스(CLI, 웹, API) 지원 및 클라우드 배포 용이성. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   개발-배포 간 에이전트 로직 일관성 유지. ([출처: Google Developers Blog](https://developers.googleblog.com))
*   **평가 및 디버깅:**
    *   시나리오 테스트, 품질 평가를 위한 도구 제공. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   로깅/디버깅 기능 활용. ([출처: Google Developers Blog](https://developers.googleblog.com))

**결론:** ADK는 에이전트 개발부터 통합, 배포까지 전 주기를 지원하는 핵심 플랫폼입니다. ([출처: Google Developers Blog](https://developers.googleblog.com), [ADK 문서](https://developers.googleblog.com))

### 4.2. Google Agent2Agent (A2A)의 역할

Google A2A는 **에이전트 상호 운용성(interoperability)**을 위한 개방형 프로토콜입니다. ([출처: Google Developers Blog](https://developers.googleblog.com), [A2A 문서](https://developers.googleblog.com))

*   **이기종 에이전트 통신 표준화:**
    *   서로 다른 환경/언어로 구현된 에이전트 간 공통 규약 제공. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   메시지, 작업 정의, 상태 업데이트, 인증 방식 표준화 -> 플러그 앤 플레이 통합. ([출처: Google Developers Blog](https://developers.googleblog.com), [A2A 문서](https://developers.googleblog.com))
    *   산업 표준으로 발전 중이며, 시스템 확장성 확보. ([출처: Google Developers Blog](https://developers.googleblog.com))
*   **에이전트 능력 광고 및 검색:**
    *   **Agent Card:** JSON으로 Capabilities 광고 및 **발견(discovery)** 지원. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   동적 에이전트 풀 확장 가능.
*   **보안 및 인증:**
    *   기관 간 인증, 권한 부여 등 보안 기능 내장. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   JWT/OAuth 유사 방식 신원 확인 및 권한 범위 내 요청 처리.
    *   메시지 필터링/암호화 옵션 제공.
*   **복잡한 워크플로우의 에이전트 협력:**
    *   멀티에이전트 워크플로우 (순차/병렬) 지원. ([출처: Google Developers Blog](https://developers.googleblog.com), [A2A 문서](https://developers.googleblog.com))
    *   상태 및 **중간 산출물(artifact)** 공유. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   표준화된 **작업 객체(task object)**로 추적/관리 용이. ([출처: Google Developers Blog](https://developers.googleblog.com))
*   **미래 대비 및 표준 준수:**
    *   타 시스템과의 호환성 확보. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   이기종 플랫폼 간 원활한 통신 토대 마련. ([출처: Google Developers Blog](https://developers.googleblog.com))

**결론:** ADK가 에이전트 개발 도구라면, A2A는 에이전트 간 대화 언어를 제공합니다. 두 기술의 시너지를 통해 효율적이고 확장 가능한 시스템을 구축합니다.

## 5. 주요 처리 시나리오 예시

### 5.1. 예시: 코딩 질문 처리 흐름

**사용자 요청:** "다음 파이썬 코드를 개선해서 실행 속도를 높여줄 수 있어? 코드: ```python\n...```"

1.  **입력 수신 및 전처리:**
    *   웹 UI에서 텍스트와 코드 블록 수신.
    *   Input Parser가 코딩 관련 키워드 탐지, 코드 블록 추출.
    *   메타데이터 태깅: "도메인=코딩", "요청유형=코드 개선".
    *   관련 대화 맥락 파악.
2.  **Dispatcher 라우팅 결정:**
    *   "도메인=코딩" 신호 기반으로 `CodingAgent` 선택.
    *   `CodingAgent`의 Agent Card 확인 (파이썬 코드 최적화 능력 검증).
    *   캐시 조회 (해당 없음).
3.  **에이전트 실행 및 작업 처리:**
    *   Dispatcher가 `CodingAgent`에 작업 할당 (내부 A2A 메시지 또는 ADK 방식). ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   `CodingAgent` (ADK 구현):
        *   `optimize_code(code, goal)` 툴 함수 보유 및 LLM 프롬프트 지시.
        *   코드 특화 LLM (Codex, Codey) 호출.
        *   필요시 코드 실행/프로파일링 툴 활용 (ADK 툴).
4.  **응답 생성:**
    *   `CodingAgent` LLM이 최적화된 코드와 개선 설명 생성.
    *   결과를 Artifact 객체로 래핑하여 반환 (ADK 방식).
    *   A2A 사용 시 표준 출력 형식으로 전달, Task 완료 신호. ([출처: Google Developers Blog](https://developers.googleblog.com))
5.  **후처리 및 포맷팅:**
    *   Dispatcher가 결과 수신 후 사용자 친화적 형식으로 다듬기 (마크다운, 하이라이트).
    *   필요시 ParaphrasingAgent로 쉬운 설명 추가 (작은 LLM 활용).
6.  **응답 반환:**
    *   정리된 최종 답변을 웹 UI로 출력.
    *   Q&A 내용을 세션 컨텍스트 저장소에 기록.

### 5.2. 다른 시나리오에의 적용

*   **문화적 질의:** 지식 QA 에이전트 호출, 필요시 웹 검색 툴 사용.
*   **데이터 분석:** DataAnalyzer (데이터 처리) + Visualization (그래프 생성) + ReportGenerator (요약) 에이전트 협업.
*   **이미지 요청:** VisionAgent (이미지 분석) -> 결과 텍스트 설명 -> 추가 질문 시 QA 에이전트로 전환 (컨텍스트 유지).

**목표:** 어떤 종류의 요청에도 시스템이 유연하게 적응하여 최적의 에이전트 파이프라인을 선택하고 응답을 제공합니다.

## 6. 성능 최적화 전략

*   **경량 모델 활용 및 모델 믹스:**
    *   간단 작업은 소형 모델/Rule-based 로직 사용.
    *   ADK 모델 유연성 활용 (Gemini vs LiteLLM). ([출처: Google Developers Blog](https://developers.googleblog.com), [ADK 문서](https://developers.googleblog.com))
*   **병렬 처리와 비동기화:**
    *   독립 작업 동시 실행 (멀티스레드/비동기 I/O).
    *   A2A 기반 병렬 에이전트 실행 관리. ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   비동기 큐 도입 (스트리밍 중 상호작용).
*   **캐싱과 재활용:**
    *   유사 질문 응답, 자주 쓰는 중간 결과 캐싱.
    *   입력 해시(코드, 이미지 특징) 기반 캐싱.
*   **컨텍스트 최소화 및 토큰 최적화:**
    *   필요한 컨텍스트만 에이전트에게 전달 (프롬프트 최적화).
    *   에이전트별 시스템 프롬프트/지시어 설계 (불필요 작업 방지).
*   **자원 스케줄링 및 스케일 아웃:**
    *   GPU/CPU 자원 효율적 스케줄링, 비활성 에이전트 언로드.
    *   컨테이너 오케스트레이션 (쿠버네티스) 기반 오토스케일링.
*   **Profiling과 지속적 최적화:**
    *   성능 로깅 및 프로파일링으로 병목 식별.
    *   ADK 평가 도구 활용, 정기적 벤치마크 및 튜닝. ([출처: Google Developers Blog](https://developers.googleblog.com))

**목표:** 높은 응답 속도와 처리량을 유지하면서 복잡한 작업을 안정적으로 수행하고, 효율적인 자원 사용을 달성합니다.

## 7. 보안 고려 사항

*   **권한 분리와 샌드박싱:**
    *   에이전트별 행동 제한.
    *   코드 실행은 안전한 샌드박스 환경 (Docker, seccomp) 사용.
    *   파일 시스템/네트워크 접근 엄격 통제.
    *   DB 접근 권한 최소화.
*   **프롬프트 안전장치 및 검열:**
    *   시스템 레벨 Content Filter 적용 (부적절 출력 차단).
    *   에이전트 지시문에 role 제한 명시 (악성 지시 방지). ([출처: Google Developers Blog](https://developers.googleblog.com))
    *   정책 프롬프트 + 후단 검열기 (1차/2차 방어벽).
*   **A2A 인증 및 암호화:**
    *   A2A 기본 인증/인가 메커니즘 적용. ([출처: Google Developers Blog](https://developers.googleblog.com))
