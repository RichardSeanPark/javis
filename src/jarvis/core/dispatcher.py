"""
중앙 디스패처 및 라우팅 로직
"""

from google.adk.agents import LlmAgent
# from google.adk.models import LlmConfig # 더 이상 사용되지 않음
from ..components.input_parser import InputParserAgent
from pydantic import Field # Field 임포트 추가
from ..models.input import ParsedInput # ParsedInput 임포트 추가
from typing import Optional # Optional 임포트 추가

class JarvisDispatcher(LlmAgent):
    """
    Jarvis AI 프레임워크의 중앙 디스패처.
    요청을 분석하고 적절한 전문 에이전트로 라우팅합니다.
    """
    # 클래스 변수로 필드 선언 (Pydantic 스타일)
    input_parser: InputParserAgent = Field(default_factory=InputParserAgent)
    sub_agents: dict = Field(default_factory=dict)
    # 추가: 현재 요청 처리 상태를 저장할 인스턴스 변수 (타입 힌트)
    current_parsed_input: Optional[ParsedInput] = None
    current_original_language: Optional[str] = None

    def __init__(self):
        """JarvisDispatcher 초기화"""
        super().__init__(
            name="JarvisDispatcher",
            description="Central dispatcher for the Jarvis AI Framework. Analyzes requests and routes them to the appropriate specialized agent.",
            model="gemini-2.0-flash-exp" # 모델 이름 직접 전달
        )
        # 초기화는 Field의 default_factory에서 처리됨
        # self.input_parser = InputParserAgent() # 제거
        # self.sub_agents = {} # 제거
        # TODO: 추후 Agent Hub 클라이언트 초기화 로직 추가

    def register_agent(self, agent: LlmAgent):
        """하위 에이전트를 디스패처에 등록합니다."""
        if not isinstance(agent, LlmAgent):
            raise TypeError("Registered agent must be an instance of LlmAgent or its subclass.")
        if not agent.name:
            raise ValueError("Registered agent must have a valid name.")
        if agent.name in self.sub_agents:
            # TODO: 로깅 라이브러리를 사용하여 경고 로깅 (logging.warning 사용)
            print(f"Warning: Agent with name '{agent.name}' already registered. Overwriting.")
            # logger.warning(f"Agent with name '{agent.name}' already registered. Overwriting.") 
        self.sub_agents[agent.name] = agent
        print(f"Agent '{agent.name}' registered successfully.")

    # TODO: 3.3. 메인 처리 로직 구현 (__call__ 또는 process_request 메서드)
    async def process_request(self, user_input: str):
        """
        사용자 입력을 받아 처리하고 적절한 에이전트로 라우팅하는 메인 로직.
        
        Args:
            user_input: 사용자의 원본 입력 문자열.
        """
        # TODO: 3.3.2. self.input_parser.process_input() 호출하여 ParsedInput 객체 얻기
        parsed_input = await self.input_parser.process_input(user_input)
        # TODO: 3.3.3. ParsedInput 객체와 original_language 정보 저장
        self.current_parsed_input = parsed_input
        self.current_original_language = parsed_input.original_language if parsed_input else None # None 체크 추가
        # TODO: 3.3.4. 라우팅 결정 로직 시작
        selected_agent = None
        if self.current_parsed_input:
            # 초기 규칙 기반 라우팅 (intent 또는 domain 기준)
            # 예시: intent가 'code_generation'이거나 domain이 'coding'이면 CodingAgent 선택
            #       intent가 'question_answering'이거나 domain이 'general'이면 KnowledgeQA_Agent 선택
            # 실제 에이전트 이름은 등록 방식에 따라 달라짐 (4단계에서 정의)
            intent = self.current_parsed_input.intent
            domain = self.current_parsed_input.domain

            # TODO: 향후 CodingAgent, KnowledgeQA_Agent 등의 실제 이름으로 변경 필요
            if (intent == 'code_generation' or domain == 'coding') and 'CodingAgent' in self.sub_agents:
                selected_agent = self.sub_agents['CodingAgent']
            elif (intent == 'question_answering' or domain == 'general') and 'KnowledgeQA_Agent' in self.sub_agents:
                selected_agent = self.sub_agents['KnowledgeQA_Agent']
            # TODO: 추가적인 라우팅 규칙 또는 기본 에이전트 설정

        # TODO: 3.4. 선택된 에이전트 호출 및 컨텍스트/툴 주입
        if selected_agent:
            # TODO: 선택된 에이전트 호출 로직 (다음 단계에서 구현)
            print(f"Routing to: {selected_agent.name}") # 임시 출력
            pass 
        else:
            # TODO: 처리할 에이전트가 없을 경우의 로직 (예: 기본 에이전트 또는 에러 처리)
            print("No suitable agent found for routing.") # 임시 출력
            pass
        
        # TODO: 3.5. 결과 처리 및 반환
        # TODO: 3.6. 에러 핸들링
        # 임시 반환값
        return "Processing complete (placeholder)."

    # TODO: 3.4. 선택된 에이전트 호출 및 컨텍스트/툴 주입
    # TODO: 3.5. 결과 처리 및 반환
    # TODO: 3.6. 에러 핸들링 