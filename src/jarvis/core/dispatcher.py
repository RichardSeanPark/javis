"""
중앙 디스패처 및 라우팅 로직
"""

from google.adk.agents import LlmAgent
# from google.adk.models import LlmConfig # 더 이상 사용되지 않음
from ..components.input_parser import InputParserAgent
from pydantic import Field # Field 임포트 추가

class JarvisDispatcher(LlmAgent):
    """
    Jarvis AI 프레임워크의 중앙 디스패처.
    요청을 분석하고 적절한 전문 에이전트로 라우팅합니다.
    """
    # 클래스 변수로 필드 선언 (Pydantic 스타일)
    input_parser: InputParserAgent = Field(default_factory=InputParserAgent)
    sub_agents: dict = Field(default_factory=dict)

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
        # TODO: 3.3.4. 라우팅 결정 로직 시작
        # TODO: 3.4. 선택된 에이전트 호출 및 컨텍스트/툴 주입
        # TODO: 3.5. 결과 처리 및 반환
        # TODO: 3.6. 에러 핸들링
        pass

    # TODO: 3.4. 선택된 에이전트 호출 및 컨텍스트/툴 주입
    # TODO: 3.5. 결과 처리 및 반환
    # TODO: 3.6. 에러 핸들링 