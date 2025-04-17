"""
중앙 디스패처 및 라우팅 로직
"""

from google.adk.agents import LlmAgent, Agent
# from google.adk.models import LlmConfig # 더 이상 사용되지 않음
from ..components.input_parser import InputParserAgent
from pydantic import Field # Field 임포트 추가
from ..models.input import ParsedInput # ParsedInput 임포트 추가
from typing import Optional, List, Dict, Any # Import List, Any
from google.genai.types import GenerateContentResponse # 새로운 SDK 경로

class JarvisDispatcher(LlmAgent):
    """
    Jarvis AI 프레임워크의 중앙 디스패처.
    요청을 분석하고 적절한 전문 에이전트로 라우팅합니다. (ADK 자동 위임 활용)
    """
    # 클래스 변수로 필드 선언 (Pydantic 스타일)
    input_parser: InputParserAgent = Field(default_factory=InputParserAgent)
    sub_agents: dict = Field(default_factory=dict)
    # 추가: 현재 요청 처리 상태를 저장할 인스턴스 변수 (타입 힌트)
    current_parsed_input: Optional[ParsedInput] = None
    current_original_language: Optional[str] = None
    # Make self.tools a list managed by the instance
    tools: List[Agent] = Field(default_factory=list)
    # Pydantic 필드로 llm 선언 (LlmAgent가 내부적으로 사용할 것으로 기대)
    llm: Any = None # 테스트에서 모킹할 수 있도록 Any 타입 사용 및 기본값 None 설정

    def __init__(self, **kwargs):
        """JarvisDispatcher 초기화"""
        instruction = (
            "You are the central dispatcher for the Jarvis AI Framework. "
            "Your primary role is to understand the user's request (provided as input) and delegate it to the most suitable specialized agent available in your tools. "
            "Examine the descriptions of the available agents (tools) to make the best routing decision. "
            "Do not attempt to fulfill the request yourself; focus solely on delegation. "
            "If multiple agents seem suitable, choose the best one. If no agent is suitable, indicate that routing is not possible."
        )
        super().__init__(
            name="JarvisDispatcher",
            description="Central dispatcher for the Jarvis AI Framework using ADK's automatic delegation based on sub-agent descriptions.",
            model="gemini-2.0-flash-exp",
            instruction=instruction,
        )
        # Ensure self.tools is initialized
        self.tools = []
        # 초기화는 Field의 default_factory에서 처리됨
        # self.input_parser = InputParserAgent() # 제거
        # self.sub_agents = {} # 제거
        # TODO: 추후 Agent Hub 클라이언트 초기화 로직 추가

    def register_agent(self, agent: Agent):
        """하위 에이전트를 디스패처에 등록하고 tools 리스트를 업데이트합니다."""
        if not isinstance(agent, Agent):
            raise TypeError("Registered agent must be an instance of Agent or its subclass.")
        if not agent.name:
            raise ValueError("Registered agent must have a valid name.")

        is_overwriting = agent.name in self.sub_agents
        if is_overwriting:
            print(f"Warning: Agent with name '{agent.name}' already registered. Overwriting.")
            # Remove the old agent from tools list
            self.tools = [tool for tool in self.tools if tool.name != agent.name]

        self.sub_agents[agent.name] = agent
        # Add the new agent to the tools list
        self.tools.append(agent)
        print(f"Agent '{agent.name}' registered and added to tools list for ADK delegation.")

    async def process_request(self, user_input: str) -> str: # Add return type hint
        """
        사용자 입력을 받아 파싱하고, ADK 자동 위임을 통해 적절한 에이전트로 라우팅 후 결과를 반환합니다.
        """
        # 1. Parse Input
        parsed_input = await self.input_parser.process_input(user_input)
        self.current_parsed_input = parsed_input
        self.current_original_language = parsed_input.original_language if parsed_input else None

        if not self.current_parsed_input:
            # TODO: Proper error handling/logging
            print("Input parsing failed. Cannot proceed.")
            return "Error: Input parsing failed."

        # Use english_text for LLM interaction
        llm_input_text = self.current_parsed_input.english_text
        print(f"Dispatcher received english text: {llm_input_text}")
        print(f"Attempting delegation using ADK LlmAgent's capabilities with {len(self.tools)} registered tool(s)...")

        # 2. ADK Delegation Logic
        try:
            # Use the agent's llm instance configured by LlmAgent __init__
            response = await self.llm.generate_content_async(
                llm_input_text,
                tools=self.tools # Pass registered agents for delegation
            )

            # Extract text response, acknowledging potential complexities with function call handling
            final_response_text = "No textual response generated." # Default
            if isinstance(response, GenerateContentResponse) and response.parts:
                text_parts = [part.text for part in response.parts if hasattr(part, 'text')]
                if text_parts:
                    final_response_text = "\n".join(text_parts)
                
                # Log if function calls were made (for debugging/future implementation)
                function_calls = [part.function_call for part in response.parts if hasattr(part, 'function_call')]
                if function_calls:
                     print(f"ADK LLM responded with function call(s): {function_calls}. Further handling might be needed.")

            print(f"Dispatcher processing finished. Raw English Response: {final_response_text}")
            # TODO: Step 6 - Pass English result to ResponseGenerator
            return final_response_text # Return English text

        except Exception as e:
            # TODO: Proper error handling and logging
            print(f"Error during dispatcher processing: {e}")
            # Consider traceback.format_exc() for more details in logging
            return f"Error during processing request: {e}"

    # TODO: 3.4. 선택된 에이전트 호출 및 컨텍스트/툴 주입
    # TODO: 3.5. 결과 처리 및 반환
    # TODO: 3.6. 에러 핸들링 