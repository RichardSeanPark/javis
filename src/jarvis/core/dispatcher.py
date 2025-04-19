"""
중앙 디스패처 및 라우팅 로직
"""

from google.adk.agents import LlmAgent, BaseAgent as Agent
# from google.adk.models import LlmConfig # 더 이상 사용되지 않음
from ..components.input_parser import InputParserAgent
# from ..components.response_generator import ResponseGenerator # Import ResponseGenerator - 주석 처리
# from ..core.context_manager import ContextManager # Import ContextManager - 주석 처리
from pydantic import Field # Field 임포트 추가
from ..models.input import ParsedInput # ParsedInput 임포트 추가
from typing import Optional, List, Dict, Any, AsyncGenerator # Import List, Any, AsyncGenerator
# import google.generativeai as genai # ADK 코드와 일치시키기 위해 주석 처리
import google.genai as genai # ADK 코드에서 사용하는 google.genai 임포트
# from google.generativeai.types import GenerateContentResponse # 경로 변경
from google.genai.types import GenerateContentResponse # google.genai 경로 사용
import logging # 로깅 추가
import os # 환경 변수 사용 위해 추가
import dotenv # .env 파일 로드 위해 추가
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext # 수정된 경로
from google.adk.events import Event # 수정된 경로
# from google.generativeai import Content, Part # google.generativeai 에서 직접 임포트 시도 -> 실패
from google.genai.types import Content, Part # ADK 코드와 일치하는 google.genai.types 경로 사용
# from typing import AsyncGenerator # typing 모듈에서 가져옴 (이미 위에서 임포트)
from typing_extensions import override # 수정된 경로
import httpx # httpx 임포트 추가
import uuid # task_id 생성을 위해 추가
from common.types import Task, TaskStatus, TaskState # <<< TaskResult 제거
# from google_a2a.client import A2AClient # A2A 클라이언트 임포트 (가정) - httpx 직접 사용

# Import the agents to be registered
from ..agents.coding_agent import CodingAgent
from ..agents.qa_agent import KnowledgeQA_Agent

# Import available tools and specific tools
from ..tools import available_tools, translate_tool, web_search_tool, code_execution_tool # Added tool imports
from google.adk.tools import BaseTool # Import BaseTool for type hinting

logger = logging.getLogger(__name__) # 로거 설정

# .env 파일 로드 (모듈 로드 시점에 한 번 실행)
dotenv.load_dotenv()

# API 키 설정 시도
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    try:
        # genai.configure가 존재하면 API 키 설정 시도
        genai.configure(api_key=API_KEY)
        logger.info("Successfully configured genai with API key.")
    except AttributeError:
        logger.warning("genai.configure does not exist. Relying on Client() to pick up credentials from environment.")
    except Exception as e:
        logger.error(f"Error configuring genai with API key: {e}")
else:
    logger.warning("GEMINI_API_KEY not found in environment variables. LLM client initialization might fail.")

DEFAULT_MODEL_NAME = os.getenv("VERTEX_MODEL_NAME", "gemini-1.5-flash-latest")
DEFAULT_INSTRUCTION = (
    "You are the central dispatcher for the Jarvis AI Framework. "
    "Your primary role is to understand the user's request (provided as input) and delegate it to the most suitable specialized agent available in your tools. "
    "Examine the descriptions of the available agents (tools) to make the best routing decision. "
    "Provide ONLY the name of the single best agent to delegate to, or 'NO_AGENT' if none are suitable. Do not add any explanation." 
    "\n\nAvailable Agents:\n" 
    # Tool descriptions will be appended dynamically
)

# Agent Hub URL 설정 (환경 변수 또는 기본값)
AGENT_HUB_DISCOVER_URL = os.getenv("AGENT_HUB_DISCOVER_URL", "http://localhost:8001/discover") # Agent Hub URL 추가

class JarvisDispatcher(LlmAgent):
    """
    Central dispatcher for the Jarvis AI Framework.
    Analyzes requests and routes them to the appropriate specialized agent.
    """
    # Declare fields using Pydantic Field
    model: str = Field(default=DEFAULT_MODEL_NAME) # Explicitly declare model field
    input_parser: InputParserAgent = Field(default_factory=InputParserAgent)
    sub_agents: Dict[str, Agent] = Field(default_factory=dict)
    # response_generator: ResponseGenerator = Field(default_factory=ResponseGenerator) # 주석 처리
    # context_manager: ContextManager = Field(default_factory=ContextManager) # 주석 처리
    llm_clients: Dict[str, Any] = Field(default_factory=dict, exclude=True)
    agent_tool_map: Dict[str, List[BaseTool]] = Field(default_factory=dict) # Added agent_tool_map
    current_parsed_input: Optional[ParsedInput] = None
    current_original_language: Optional[str] = None
    http_client: httpx.AsyncClient = Field(default=None, exclude=True) # HTTP 클라이언트 필드 추가

    def __init__(self, **kwargs):
        """
        Initializes the JarvisDispatcher.
        """
        # Ensure default name and description are in kwargs before calling super
        kwargs.setdefault('name', "JarvisDispatcher")
        kwargs.setdefault('description', "Central dispatcher for the Jarvis AI Framework. Analyzes requests and routes them to the appropriate specialized agent.")

        # Pass kwargs (including potentially defaulted name/description) to super().__init__
        super().__init__(**kwargs)

        # Ensure default model is set if not provided in kwargs
        # (super init should handle model from kwargs, but set default if missing)
        if 'model' not in kwargs:
            self.model = DEFAULT_MODEL_NAME
            logger.info(f"Dispatcher model not provided in kwargs, using default: {self.model}")
        else:
             # super().__init__ already set self.model from kwargs if present
             logger.info(f"Dispatcher model initialized to: {self.model}")

        # Update instruction after super init if needed
        self.instruction = DEFAULT_INSTRUCTION

        # Define the tool map for agents BEFORE registering them
        self.agent_tool_map = {
            "CodingAgent": [code_execution_tool],
            "KnowledgeQA_Agent": [web_search_tool, translate_tool],
            # Add other agents and their specific tools here
        }
        # logger.info(f"Agent tool map defined: { {k: [t.name for t in v] for k, v in self.agent_tool_map.items()} }") # Log tool names for readability - REMOVED DUE TO INIT ORDER ISSUE

        # Register agents after ensuring self.sub_agents exists (due to default_factory)
        # The tools list for the dispatcher itself now includes agents for delegation decision
        self.register_agent(CodingAgent())
        self.register_agent(KnowledgeQA_Agent())

        # Initialize LLM client for the dispatcher's model
        self._initialize_llm_client(self.model)

        # Initialize HTTP client
        self.http_client = httpx.AsyncClient() # HTTP 클라이언트 초기화
        logger.info(f"Initialized httpx.AsyncClient.")

        # --- Init Log ---
        logger.info(f"Initialized JarvisDispatcher (as LlmAgent).")
        logger.info(f" - Name: {self.name}")
        logger.info(f" - Description: {self.description[:50]}...")
        logger.info(f" - Dispatcher Model: {self.model}")
        logger.info(f" - Initial Tools: {self.tools}")
        logger.info(f" - LLM Client for dispatcher ({self.model}): {self.llm_clients.get(self.model)}")
        # --- Init Log End ---

    def _initialize_llm_client(self, model_name: str):
        """주어진 모델 이름에 대한 LLM 클라이언트를 초기화하고 llm_clients에 저장합니다."""
        if not model_name or "mock-model" in model_name:
            logger.info(f"Skipping LLM client initialization for model/key: {model_name}")
            return

        if model_name not in self.llm_clients:
            # API 키가 있는지 먼저 확인
            if not API_KEY:
                logger.error(f"Cannot initialize LLM client for {model_name}: GEMINI_API_KEY is missing.")
                self.llm_clients[model_name] = None
                return
            try:
                # Client() 생성 시 API 키 명시적 전달
                client = genai.Client(api_key=API_KEY)
                self.llm_clients[model_name] = client
                logger.info(f"Successfully initialized LLM client (genai.Client) with API key, associated with key: {model_name}, Type: {type(client)}")
            except Exception as e:
                logger.error(f"Failed to initialize LLM client (genai.Client) with API key, associated with key {model_name}: {e}")
                self.llm_clients[model_name] = None

    def get_llm_client(self, model_name: str) -> Any:
        """지정된 모델 이름에 대한 초기화된 LLM 클라이언트를 반환합니다."""
        if model_name not in self.llm_clients:
            logger.warning(f"LLM client for model '{model_name}' not pre-initialized. Attempting initialization.")
            self._initialize_llm_client(model_name)

        client = self.llm_clients.get(model_name)
        if client is None:
             logger.error(f"LLM client for model '{model_name}' is not available (initialization might have failed).")
        return client

    def register_agent(self, agent: Agent):
        """하위 에이전트를 디스패처에 등록하고, 필요한 LLM 클라이언트를 초기화하며, tools 리스트를 업데이트합니다."""
        if not isinstance(agent, Agent):
            raise TypeError("Registered agent must be an instance of Agent or its subclass.")
        if not agent.name:
            raise ValueError("Registered agent must have a valid name.")

        if isinstance(agent, LlmAgent) and agent.model:
             self._initialize_llm_client(agent.model)

        is_overwriting = agent.name in self.sub_agents

        # Update sub_agents dictionary first
        self.sub_agents[agent.name] = agent

        # Rebuild the tools list from the updated sub_agents dictionary
        # Ensure the dispatcher itself isn't accidentally added as a tool
        updated_tools = list(self.sub_agents.values())

        # Assign the newly built list to self.tools
        self.tools = updated_tools

        # Log the registration
        if is_overwriting:
            logger.warning(f"Agent with name \'{agent.name}\' overwritten.")
        logger.info(f"Agent '{agent.name}' (type: {type(agent)}, model: {getattr(agent, 'model', 'N/A')}) registered/updated. Current tools: {[getattr(t, 'name', 'N/A') for t in self.tools]}")

    async def process_request(self, user_input: str) -> str:
        """
        사용자 입력을 받아 파싱하고, 직접 LLM 호출을 통해 위임할 에이전트 이름을 결정한 후,
        결과 메시지를 반환합니다. (실제 에이전트 호출은 외부 Runner가 담당 가정)
        A2A 동적 검색 로직 placeholder 추가.
        """
        # 1. Parse Input
        if not self.input_parser:
             logger.error("Input parser not initialized!")
             return "Error: Input parser not available."
        parsed_input = await self.input_parser.process_input(user_input)
        self.current_parsed_input = parsed_input
        self.current_original_language = parsed_input.original_language if parsed_input else None

        if not self.current_parsed_input:
            logger.error("Input parsing failed. Cannot proceed.")
            return "Error: Input parsing failed."

        llm_input_text = self.current_parsed_input.english_text
        logger.info(f"Dispatcher deciding delegation for: {llm_input_text[:100]}...")

        # 2. Prepare Prompt for Delegation Decision
        # Generate the list of available tools/agents for the prompt
        tool_descriptions = "\n".join([
            f"- {getattr(tool, 'name', 'N/A')}: {getattr(tool, 'description', 'N/A')}"
            for tool in self.tools
        ])
        # Combine instruction, tool descriptions, and user query
        prompt = f"{self.instruction}\n{tool_descriptions}\n\nUser Request: {llm_input_text}"
        logger.debug(f"Dispatcher Prompt:\n{prompt}")

        # 3. Call LLM for Delegation Decision
        dispatcher_llm_client = self.get_llm_client(self.model)
        if not dispatcher_llm_client:
            logger.error(f"LLM client for dispatcher (model key: {self.model}) not initialized!")
            return "Error: LLM client not available for dispatcher."

        delegated_agent_name = "NO_AGENT" # Default

        try:
            logger.info(f"Calling dispatcher's LLM (model={self.model}) via Client for delegation decision.")
            # Client 객체를 사용하여 generate_content_async 호출 (모델 이름 전달 필요)
            # 수정: python-genai 1.11.0 방식인 aio.models 사용
            response = await dispatcher_llm_client.aio.models.generate_content(
                model=self.model, # 사용할 모델 이름 명시 (GenerativeModel과 달리 Client 사용 시 모델 지정 불필요할 수 있음 - 확인 필요)
                contents=[Content(parts=[Part(text=prompt)])] # Content 객체 리스트로 전달
            )

            logger.debug(f"Raw Delegation LLM Response type: {type(response)}")
            logger.debug(f"Raw Delegation LLM Response: {response}")

            # Extract the agent name from the response
            if response and hasattr(response, 'text'):
                # Assuming response.text directly contains the agent name or NO_AGENT
                potential_agent_name = response.text.strip()
                # Simple validation: check if the name exists in sub_agents
                if potential_agent_name in self.sub_agents:
                    delegated_agent_name = potential_agent_name
                    logger.info(f"Dispatcher LLM decided to delegate to internal agent: {delegated_agent_name}")
                elif potential_agent_name == "NO_AGENT":
                     logger.info("Dispatcher LLM indicated no suitable internal agent found.")
                     # --- A2A Discovery Placeholder ---
                     logger.info("Attempting A2A agent discovery...")
                     # Define needed capability based on parsed_input (example)
                     needed_capability = f"Handle intent '{self.current_parsed_input.intent}' in domain '{self.current_parsed_input.domain}'"
                     discovered_agents = await self._discover_a2a_agents(needed_capability)
                     if discovered_agents:
                         # TODO (Step 7): Implement logic to select the best A2A agent
                         # For now, just log the discovery
                         logger.info(f"Discovered {len(discovered_agents)} potential A2A agents.")
                         # Placeholder: Select the first discovered agent for now
                         # selected_a2a_agent_card = discovered_agents[0]
                         # delegated_agent_name = f"A2A:{selected_a2a_agent_card.get('name', 'Unknown')}" # Mark as A2A
                         # logger.info(f"Selected A2A agent (placeholder): {delegated_agent_name}")
                         pass # Keep delegated_agent_name as "NO_AGENT" until selection logic is implemented
                     else:
                         logger.info("No suitable A2A agents discovered.")
                     # --- End A2A Discovery Placeholder ---

                else:
                    logger.warning(f"Dispatcher LLM returned an unknown agent name: '{potential_agent_name}'. Treating as NO_AGENT.")
                    delegated_agent_name = "NO_AGENT"

            else:
                logger.error(f"Failed to get valid text response from delegation LLM. Response: {response}")
                delegated_agent_name = "NO_AGENT"

        except Exception as e:
            logger.error(f"Error during LLM call for delegation: {e}", exc_info=True)
            delegated_agent_name = "NO_AGENT" # Ensure default on error

        # 4. Return Result (Placeholder - Actual invocation happens elsewhere)
        # Based on the decided agent, prepare a message or structure for the runner
        if delegated_agent_name != "NO_AGENT":
            # TODO: Refine this return message/structure based on Runner needs
            # return f"Delegating task to agent: {delegated_agent_name}"
            # --- Triggering Agent Call (Simulation/Placeholder) ---
            # In a real scenario, the runner would handle this based on the name.
            # Here, we simulate the start of the invocation process for logging.
            if delegated_agent_name.startswith("A2A:"):
                 logger.info(f"Dispatcher requests Runner to invoke A2A agent: {delegated_agent_name.split(':')[1]}")
                 # Placeholder for A2A call structure
                 # task_input = self.current_parsed_input.english_text # Or more structured input
                 # result = await self._call_a2a_agent(selected_a2a_agent_card, task_input)
                 # return f"A2A agent execution result (placeholder): {result}"
                 return "A2A agent invocation requested (Runner should handle)." # Placeholder return
            elif delegated_agent_name in self.sub_agents:
                 logger.info(f"Dispatcher requests Runner to invoke internal agent: {delegated_agent_name}")
                 # The Runner would typically call self.sub_agents[delegated_agent_name].invoke()
                 return f"Internal agent invocation requested: {delegated_agent_name}" # Placeholder return
            else: # Should not happen if logic above is correct
                 logger.error(f"Internal error: Invalid delegated_agent_name '{delegated_agent_name}' reached return stage.")
                 return "Error: Internal dispatcher error during agent selection."
        else:
            logger.info("No suitable agent found (internal or A2A).")
            # TODO: Define behavior when no agent can handle the request
            return "I cannot find a suitable agent to handle your request at this time."

        # --- Old Return Logic (commented out) ---
        # # 5. (Optional) Generate Final Response (moved to ResponseGenerator/Runner)
        # # english_result = f"Task delegated to {delegated_agent_name}." # Placeholder result
        # # final_response = await self.response_generator.generate_response(
        # #     english_result, self.current_original_language or 'en'
        # # )
        # # return final_response
        # return f"Delegation decision: {delegated_agent_name}" # Simplified return for now

    @override
    async def invoke(self, ctx: InvocationContext):
        # Dispatcher 자체는 직접 invoke되지 않아야 함 (Runner가 process_request를 사용하도록)
        # 또는 process_request를 호출하도록 구현?
        # 여기서는 에러를 발생시켜 잘못된 사용을 방지
        raise NotImplementedError("JarvisDispatcher should not be invoked directly. Use process_request or run via Runner.")

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
         # Runner가 agent.run_async를 호출할 때 이 메소드가 실행될 수 있음.
         # process_request를 호출하고 결과를 이벤트로 변환하는 방식으로 구현 가능
         # user_input = ctx.get_last_user_message_text() # AttributeError 발생 지점
         user_input = None
         # InvocationContext 구조 변경 가능성에 대비하여 안전하게 접근
         if ctx.user_content and hasattr(ctx.user_content, 'parts') and ctx.user_content.parts:
             if hasattr(ctx.user_content.parts[0], 'text'):
                 user_input = ctx.user_content.parts[0].text

         if not user_input:
              logger.warning("_run_async_impl called without user input text in context.")
              # 수정: Event 생성자 사용
              yield Event(
                   author=self.name,
                   content=Content(parts=[Part(text="Error: Could not get user input from context.")])
                   # invocation_id 등 다른 필수 필드가 있다면 추가 필요
              )
              return

         result_text = await self.process_request(user_input)

         # 수정: Event 생성자 사용
         yield Event(
              author=self.name,
              content=Content(parts=[Part(text=result_text)])
              # invocation_id 등 다른 필수 필드가 있다면 추가 필요
         )

    # --- A2A Discovery and Call Methods ---
    async def _discover_a2a_agents(self, capability: str) -> List[Dict[str, Any]]:
        """Agent Hub에서 주어진 능력을 가진 에이전트를 검색합니다."""
        if not self.http_client:
            logger.error("HTTP client not initialized for A2A discovery.")
            return []
        try:
            logger.info(f"Discovering A2A agents with capability: {capability} from {AGENT_HUB_DISCOVER_URL}")
            response = await self.http_client.get(AGENT_HUB_DISCOVER_URL, params={"capability": capability})
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            discovered_agents = response.json()
            logger.info(f"Discovered {len(discovered_agents)} A2A agents.")
            return discovered_agents
        except httpx.RequestError as exc:
            logger.error(f"A2A discovery request failed: {exc}")
            return []
        except httpx.HTTPStatusError as exc:
            logger.error(f"A2A discovery failed with status {exc.response.status_code}: {exc.response.text}")
            return []
        except Exception as e:
            logger.error(f"An unexpected error occurred during A2A discovery: {e}")
            return []

    async def _call_a2a_agent(self, agent_card: Dict[str, Any], task_input: Any) -> Any:
        """선택된 A2A 에이전트를 호출합니다. (google-a2a-python 라이브러리 사용)"""
        agent_name = agent_card.get('name', 'Unknown A2A Agent')
        agent_endpoint = agent_card.get('a2a_endpoint') # Agent Card에서 엔드포인트 URL 가져오기 (키 이름 확인 필요)

        if not agent_endpoint:
            logger.error(f"A2A agent '{agent_name}' card does not contain an endpoint URL.")
            return f"Error: Missing endpoint for A2A agent '{agent_name}'."

        if not self.http_client:
             logger.error("HTTP client not initialized for A2A call.")
             return "Error: HTTP client not available."

        task_id = str(uuid.uuid4())
        # Task 객체 생성 (common.types.Task 모델 사용)
        try:
            # 실제 Task 모델에 맞게 수정
            initial_status = TaskStatus(state=TaskState.SUBMITTED) # TaskStatus 객체 생성
            a2a_task = Task(
                id=task_id, # 'id' 필드 사용
                status=initial_status # 생성된 TaskStatus 객체 할당
                # task_type 및 input 필드는 Task 모델에 없으므로 제거
            )
            task_payload = a2a_task.model_dump() # Pydantic V2의 model_dump() 사용
        except Exception as e:
            logger.error(f"Failed to create or serialize A2A Task object: {e}")
            import traceback
            traceback.print_exc() # 디버깅을 위해 스택 트레이스 추가
            return f"Error: Internal error preparing A2A task for '{agent_name}'."


        try:
            logger.info(f"Calling A2A agent '{agent_name}' at {agent_endpoint} with task_id: {task_id}")
            # google-a2a-python 라이브러리가 자체 클라이언트를 제공하지 않는 경우 httpx 사용
            # 여기서는 httpx를 사용하여 POST 요청을 보낸다고 가정
            response = await self.http_client.post(
                agent_endpoint,
                json=task_payload, # 직렬화된 Task 객체 사용
                timeout=60.0 # 타임아웃 설정 (적절히 조정)
            )
            response.raise_for_status()

            # 응답을 TaskResult 객체로 파싱 (또는 Task 객체 업데이트)
            result_data = response.json()
            # Pydantic 모델이라고 가정하고 .parse_obj() 사용 - model_validate 사용 권장
            # task_response = Task.parse_obj(result_data) # <<< Task 객체로 파싱
            task_response = Task.model_validate(result_data) # Pydantic V2의 model_validate 사용

            logger.info(f"Received task response from A2A agent '{agent_name}' with status: {task_response.status.state}") # <<< Task 상태 로깅

            if task_response.status.state == TaskState.COMPLETED: # <<< Task 상태 확인
                # 결과 추출 로직: artifacts 리스트의 첫 번째 artifact의 첫 번째 text part를 반환 (예시)
                if task_response.artifacts and task_response.artifacts[0].parts:
                    first_part = task_response.artifacts[0].parts[0]
                    # Check if the part is a TextPart before accessing .text
                    if hasattr(first_part, 'text'): 
                        return first_part.text
                    elif hasattr(first_part, 'data'): # Handle DataPart if necessary
                         logger.warning(f"A2A task from '{agent_name}' completed with DataPart, returning as string.")
                         return str(first_part.data)
                logger.warning(f"A2A task from '{agent_name}' completed but no suitable output artifact found.")
                return f"A2A task '{agent_name}' completed without text output."
            else:
                # error_message = task_result.error or f"Task failed with status {task_result.status}" # <<< TaskResult 대신 Task 상태 사용
                error_message = f"Task failed with status {task_response.status.state}" # <<< Task 상태 기반 오류 메시지
                # 실패 시 Task 상태 메시지 포함 (존재하는 경우)
                if task_response.status.message and task_response.status.message.parts:
                    first_part = task_response.status.message.parts[0]
                    # Check if the part is a TextPart before accessing .text
                    if hasattr(first_part, 'text'):
                         error_message += f": {first_part.text}"

                logger.error(f"A2A task failed for agent '{agent_name}': {error_message}")
                return f"Error from A2A agent '{agent_name}': {error_message}"

        except httpx.RequestError as exc:
            logger.error(f"A2A call request to '{agent_name}' failed: {exc}")
            return f"Error: Failed to connect to A2A agent '{agent_name}'."
        except httpx.HTTPStatusError as exc:
            logger.error(f"A2A call to '{agent_name}' failed with status {exc.response.status_code}: {exc.response.text}")
            return f"Error: A2A agent '{agent_name}' returned status {exc.response.status_code}."
        except Exception as e:
            # Pydantic validation error 등 포함
            logger.error(f"An unexpected error occurred during A2A call to '{agent_name}': {e}")
            import traceback
            traceback.print_exc() # 디버깅을 위해 스택 트레이스 추가
            return f"Error: Unexpected error during communication with A2A agent '{agent_name}'."
    # --- End A2A Methods ---

# Type alias 등은 BaseAgent와 호환되도록 확인/수정 필요 (현재 코드에서는 직접 사용 안함) 