## Jarvis AI 프레임워크 개발 구현 계획 (Step-by-Step & Vibe 코딩 활용)

AI를 활용한 Vibe 코딩 방식으로 Jarvis AI 프레임워크를 구현하기 위한 가장 효율적이고 체계적인 Step-by-Step 진행 방법을 상세히 설명드리겠습니다. 핵심은 **명확한 계획 수립**, **점진적 구현 및 테스트**, **AI의 적극적인 활용**입니다.

---

**Phase 0: 준비 및 계획 수립 (Foundation)**

1.  **`PLAN.md` 작성 (핵심 설계 통합 문서):**
    *   **목표:** `ubuntu_jarvis_ai_framework_design.md`의 상세 내용과 설계 철학, 그리고 `jarvis_ai_framework_analysis.md`의 구조화된 목차 및 다이어그램을 통합하여 **하나의 실행 가능한 마스터 설계/계획 문서**를 만듭니다.
    *   **AI 활용 (Vibe Coding):**
        *   AI에게 두 문서를 제공하고, `analysis.md`의 목차 구조를 따르면서 각 섹션에 `design.md`의 상세 내용(기술 스택, ADK/A2A 활용 방식, 설계 이유 등)을 병합하도록 요청합니다.
        *   이전 논의에서 수정된 내용(예: 하이브리드 라우팅 전략, Agent Hub 역할)이 정확히 반영되었는지 AI와 함께 검토하고 다듬습니다.
    *   **산출물:** 프로젝트의 최종 목표와 설계가 명확히 기술된 `PLAN.md`. 이 문서는 프로젝트 진행 중 계속 업데이트되는 살아있는 문서(Living Document)가 됩니다.

2.  **`TODO.md` 작성 (작업 관리)**
    *   **목표:** `PLAN.md`를 기반으로 구현해야 할 주요 기능 및 컴포넌트를 **구체적인 작업 단위(Task)**로 분해하여 목록화합니다. 체크리스트 형태로 작성하여 진행 상황을 추적합니다.
    *   **AI 활용 (Vibe Coding):**
        *   AI에게 `PLAN.md`의 각 섹션(예: 3.1 입력 처리 계층, 5.2 디스패처)을 기반으로 필요한 개발 작업 목록 초안을 생성하도록 요청합니다. (예: "- [ ] 입력 파서: 텍스트 의도 분류 기능 구현", "- [ ] 디스패처: 규칙 기반 라우팅 로직 구현")
    *   **산출물:** 초기 작업 목록이 담긴 `TODO.md`. 프로젝트 진행에 따라 지속적으로 업데이트됩니다.

3.  **초기 기술 스택 확정:**
    *   `PLAN.md`에 명시된 내용을 바탕으로 사용할 구체적인 라이브러리 버전(Python, ADK, A2A 관련 패키지 등)을 결정하고 `PLAN.md` 또는 별도 `TECH_STACK.md`에 기록합니다.

4.  **프로젝트 저장소 설정:**
    *   Git 저장소를 생성하고 초기 구조를 설정합니다. (`README.md`, `.gitignore` 등)

---

**Phase 1: 기본 프레임워크 및 환경 설정 (Scaffolding)**

5.  **프로젝트 폴더 구조 생성:**
    *   `PLAN.md`의 아키텍처를 반영하여 기본 폴더 구조를 만듭니다. (예: `src/agents`, `src/tools`, `src/core` (Dispatcher, Hub 등), `config`, `tests`, `scripts`)
    *   **AI 활용 (Vibe Coding):** AI에게 제안된 아키텍처에 맞는 Python 프로젝트 폴더 구조 예시를 생성하도록 요청할 수 있습니다.

6.  **가상 환경 설정 및 ADK 설치:**
    *   Python 가상 환경을 설정하고 활성화합니다.
    *   `pip install google-adk` 명령어로 ADK를 설치하고, 초기 의존성 목록(`requirements.txt` 또는 `pyproject.toml`)을 생성합니다.

7.  **기본 환경 설정 (`.env`):**
    *   필요한 API 키 (Google API Key 등) 및 기본 설정을 위한 `.env` 파일을 생성하고 관리합니다. `.gitignore`에 `.env`를 추가합니다.

8.  **기본 ADK 실행 환경 설정:**
    *   ADK 애플리케이션의 진입점(Entry Point)이 될 간단한 Python 스크립트(예: `main.py` 또는 `run.py`)를 만듭니다. (초기에는 최소한의 Runner 및 SessionService 설정만 포함)
    *   `adk web` 명령어가 작동할 수 있도록 프로젝트 루트에 필요한 `__init__.py` 등을 설정합니다.
    *   **AI 활용 (Vibe Coding):** ADK Quickstart 또는 Tutorial [\[1\]](https://google.github.io/adk-docs/get-started/tutorial/) 코드를 참조하여 기본 Runner 및 `InMemorySessionService` 설정 코드를 생성하도록 AI에게 요청합니다.

9.  **로깅 설정:**
    *   기본적인 로깅 설정을 추가하여 개발 중 디버깅을 용이하게 합니다.

---

**Phase 2: 핵심 컴포넌트 구현 1 - 라우팅 및 관리 (Core Plumbing)**

10. **기본 Dispatcher 구현:**
    *   `PLAN.md` (5.2절)에 따라, 기본 `LlmAgent`를 상속받는 Dispatcher 클래스를 구현합니다. 초기에는 최소한의 instruction만 포함합니다.
    *   **AI 활용 (Vibe Coding):** AI에게 `PLAN.md` 설명을 기반으로 Dispatcher 클래스의 기본 구조 (init, 주요 메서드 placeholder) 생성을 요청합니다.

11. **기본 Agent Hub 구현:**
    *   `PLAN.md` (5.3절)에 따라, 에이전트 등록 및 메타데이터 관리를 위한 간단한 Agent Hub 클래스 또는 모듈을 구현합니다. 초기에는 인메모리 딕셔너리 등으로 간단하게 시작합니다. A2A Discovery 기능은 이 단계에서는 placeholder로 둡니다.

12. **기본 Session Service 확인:**
    *   `InMemorySessionService`가 제대로 동작하는지 간단한 테스트 코드로 확인합니다. (추후 필요시 Persistent Session Service로 교체)

---

**Phase 3: 핵심 컴포넌트 구현 2 - 첫 Agent & Tool (End-to-End Validation)**

13. **첫 번째 특화 에이전트 구현 (간단한 것):**
    *   `PLAN.md` (3절 도메인별 에이전트 계층)에서 가장 간단한 에이전트 하나를 선택합니다(예: 인사말 에이전트 또는 날씨 에이전트). ADK `LlmAgent` 또는 `Agent` 클래스를 사용하여 구현합니다.
    *   **AI 활용 (Vibe Coding):** ADK 튜토리얼의 `greeting_agent` 또는 `weather_agent` 코드를 참조하여 [\[1\]](https://google.github.io/adk-docs/get-started/tutorial/) , 선택한 에이전트의 기본 코드를 생성하도록 AI에게 요청합니다.

14. **첫 번째 툴 구현 (Mocked):**
    *   선택한 에이전트가 사용할 간단한 Python 함수 툴을 구현합니다. 초기에는 실제 API 호출 대신 Mock 데이터를 반환하도록 만듭니다. Docstring을 명확하게 작성합니다 (ADK 툴 정의 가이드라인 참조 [\[2\]](https://google.github.io/adk-docs/tools/)).
    *   **AI 활용 (Vibe Coding):** AI에게 특정 기능을 수행하는 Mock Python 함수(툴)와 상세한 Docstring 초안 작성을 요청합니다.

15. **Dispatcher와 첫 에이전트/툴 연동:**
    *   Dispatcher가 **규칙 기반**으로 이 첫 번째 에이전트를 호출하도록 라우팅 로직을 추가합니다.
    *   Agent Hub에 이 에이전트를 등록합니다.
    *   ADK 실행 환경에서 Dispatcher를 루트 에이전트로 설정합니다.

16. **기본 흐름 테스트:**
    *   `adk web` 또는 터미널을 사용하여 사용자 입력 -> Dispatcher -> 특화 에이전트 -> 툴 호출 -> 응답 반환까지의 **가장 기본적인 End-to-End 흐름**이 작동하는지 테스트하고 디버깅합니다.
    *   `TODO.md`에서 완료된 항목을 체크합니다.

---

**Phase 4: 도메인별 에이전트 및 툴 확장 (Feature Expansion)**

17. **주요 특화 에이전트 순차적 구현:**
    *   `PLAN.md`와 `TODO.md`를 참조하여 코딩 에이전트, 문서 작성 에이전트, QA 에이전트 등 핵심 특화 에이전트들을 **하나씩** 구현합니다.
    *   각 에이전트의 `instruction`, `description`을 명확하게 작성합니다.

18. **해당 툴 구현 및 연동 (Real APIs):**
    *   각 에이전트가 사용할 실제 툴(Python 함수)을 구현합니다. 필요시 실제 외부 API를 호출하거나 라이브러리를 사용합니다. API Key 등은 `.env`를 통해 관리합니다.
    *   구현된 툴을 해당 에이전트의 `tools` 목록에 추가합니다. Docstring 작성에 유의합니다.
    *   **AI 활용 (Vibe Coding):** 특정 API 문서를 제공하고 해당 API를 호출하는 Python 함수(툴) 코드를 생성하도록 AI에게 요청합니다. 오류 처리 로직 추가도 요청할 수 있습니다.

19. **Dispatcher 라우팅 로직 확장:**
    *   새로 추가된 에이전트를 처리하기 위해 Dispatcher의 라우팅 로직을 확장합니다. (규칙 기반 추가, ADK 자동 위임 설정 준비)

20. **개별 에이전트/툴 테스트:**
    *   추가된 에이전트와 툴이 예상대로 작동하는지 개별적으로 테스트합니다.
    *   `TODO.md`를 업데이트합니다.

---

**Phase 5: 고급 기능 구현 (Advanced Capabilities)**

21. **ADK 자동 위임 (Auto Delegation) 구현:**
    *   Dispatcher가 특정 요청에 대해 `description`이 잘 작성된 서브 에이전트(특화 에이전트)에게 자동으로 작업을 위임하도록 설정합니다. (ADK Multi-agent 문서 참조 [\[3\]](https://google.github.io/adk-docs/agents/multi-agent-systems/))
    *   **AI 활용 (Vibe Coding):** AI에게 ADK의 자동 위임 패턴을 적용하는 Dispatcher 코드 예시를 요청합니다.

22. **A2A Discovery 및 통신 구현:**
    *   Agent Hub에 **A2A Discovery 서비스** 로직을 구체화합니다. (Agent Card 검색 기능)
    *   Dispatcher가 특정 조건에서 Agent Hub에 A2A Discovery를 요청하도록 구현합니다.
    *   이기종 에이전트와의 통신을 위해 **A2A Client/Server 로직**을 구현합니다. (A2A 샘플 코드 참조 [\[4\]](https://github.com/google/A2A/blob/main-llms.txt/llms.txt)) 최소한 하나의 외부 에이전트(시뮬레이션 가능)와 A2A로 통신하는 흐름을 구현하고 테스트합니다.
    *   **AI 활용 (Vibe Coding):** A2A GitHub 저장소의 샘플 코드를 기반으로 A2A Client/Server 또는 Discovery 관련 Python 코드 스니펫 생성을 요청합니다.

23. **세션 상태 및 컨텍스트 관리 구현:**
    *   ADK의 `Session State`와 `ToolContext`를 활용하여 대화 간 메모리(예: 사용자 선호도) 및 툴 실행에 필요한 컨텍스트를 관리하는 기능을 구현합니다. (ADK Tutorial Step 4 참조 [\[1\]](https://google.github.io/adk-docs/get-started/tutorial/))

24. **보안 가드레일 구현:**
    *   ADK `callback` 함수(`before_model_callback`, `before_tool_callback` 등)를 사용하여 입력 또는 툴 실행에 대한 안전장치를 구현합니다. (ADK Tutorial Step 5, 6 참조 [\[1\]](https://google.github.io/adk-docs/get-started/tutorial/))
    *   **AI 활용 (Vibe Coding):** 특정 정책(예: 특정 단어 필터링, 특정 API 파라미터 제한)을 설명하고 이를 구현하는 ADK callback 함수 코드 생성을 요청합니다.

25. **고급 기능 테스트:**
    *   자동 위임, A2A 통신, 세션 상태, 보안 가드레일 등이 의도대로 작동하는지 테스트합니다.
    *   `TODO.md`를 업데이트합니다.

---

**Phase 6: 통합, 테스트 및 평가 (Integration & Testing)**

26. **단위 테스트 작성:**
    *   개별 툴(함수), 중요한 유틸리티 함수, 에이전트의 특정 로직에 대한 단위 테스트를 작성합니다 (`pytest` 등 활용).
    *   **AI 활용 (Vibe Coding):** 특정 함수 코드를 제공하고 이에 대한 `pytest` 단위 테스트 케이스 초안 생성을 요청합니다.

27. **통합 테스트 작성:**
    *   Dispatcher-Agent-Tool 간의 상호작용을 검증하는 통합 테스트를 작성합니다.

28. **End-to-End (E2E) 시나리오 테스트:**
    *   `PLAN.md` (또는 `analysis.md` 8절)의 주요 처리 시나리오를 기반으로 E2E 테스트 케이스를 작성하고 실행합니다. 사용자의 실제 사용 흐름을 시뮬레이션합니다.

29. **ADK 평가 도구 활용 (선택 사항):**
    *   ADK에서 제공하는 평가 프레임워크가 있다면 이를 활용하여 에이전트의 성능과 품질을 정량적으로 평가합니다. (ADK Docs - Evaluate 섹션 참조)

30. **결과 분석 및 리팩토링:**
    *   테스트 결과를 바탕으로 버그를 수정하고 코드 품질을 개선합니다(리팩토링).
    *   `TODO.md`의 테스트 관련 항목을 업데이트합니다.

---

**Phase 7: 배포 준비 및 문서화 (Packaging & Documentation)**

31. **컨테이너화 (Docker):**
    *   애플리케이션 배포를 위해 `Dockerfile`을 작성합니다.
    *   **AI 활용 (Vibe Coding):** 프로젝트 구조와 의존성을 설명하고 `Dockerfile` 초안 생성을 요청합니다.

32. **배포 스크립트/설정 준비:**
    *   목표 배포 환경(Cloud Run, GKE 등)에 맞는 배포 스크립트 또는 설정 파일을 준비합니다. (ADK Docs - Deploy 섹션 참조)

33. **최종 문서화:**
    *   `README.md`에 프로젝트 설정 방법, 실행 방법, 주요 기능 등을 상세히 기술합니다.
    *   코드 내 Docstring을 검토하고 보강합니다.
    *   `PLAN.md`를 최종 설계 문서로 확정합니다.
    *   `TODO.md`를 검토하여 완료되지 않은 작업이나 다음 단계 작업을 명확히 합니다.
    *   **AI 활용 (Vibe Coding):** 코드베이스를 분석하여 `README.md`의 특정 섹션(예: 설치 방법, API 사용법) 초안 작성을 요청합니다.

---

**Phase 8: 배포 및 반복 (Deployment & Iteration)**

34. **배포:**
    *   준비된 스크립트/설정을 사용하여 선택한 환경에 프레임워크를 배포합니다.

35. **모니터링 및 로깅:**
    *   배포된 환경에서 시스템 로그 및 성능 지표를 모니터링합니다.

36. **피드백 수집 및 반복:**
    *   (해당하는 경우) 사용자 피드백을 수집합니다.
    *   모니터링 결과와 피드백, `TODO.md`의 남은 항목을 바탕으로 다음 개발 이터레이션을 계획하고 Phase 4~7을 반복합니다.

---

**Vibe 코딩 활용 팁:**

*   **명확한 프롬프트:** AI에게 작업을 요청할 때는 `PLAN.md`의 관련 섹션, ADK/A2A 문서의 특정 개념, 코드 예시 등을 명확히 제시해야 더 좋은 결과를 얻을 수 있습니다.
*   **코드 생성 요청:** 단순히 "코드 짜줘"보다는 "ADK의 LlmAgent를 상속받고 PLAN.md 5.2절 설명을 따르는 Dispatcher 파이썬 클래스 기본 구조를 만들어줘" 와 같이 구체적으로 요청합니다.
*   **리뷰 및 검증:** AI가 생성한 코드는 반드시 개발자가 직접 리뷰하고 테스트해야 합니다. AI는 보조 도구일 뿐입니다.
*   **문서 요약/생성:** 방대한 문서를 요약하거나, 코드 기반으로 문서 초안을 작성하는 데 AI를 활용하면 효율적입니다.

이 상세한 Step-by-Step 계획과 Vibe 코딩 방식을 병행하면, 복잡한 Jarvis AI 프레임워크를 체계적이고 효율적으로 구현해 나갈 수 있을 것입니다. 각 단계의 산출물(PLAN.md, TODO.md, 코드, 테스트 등)을 명확히 관리하는 것이 중요합니다.

*[1]: https://google.github.io/adk-docs/get-started/tutorial/
[2]: https://google.github.io/adk-docs/tools/
[3]: https://google.github.io/adk-docs/agents/multi-agent-systems/
[4]: https://github.com/google/A2A/blob/main-llms.txt/llms.txt* 