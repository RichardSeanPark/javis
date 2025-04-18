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

# Import the agents to be registered
from ..agents.coding_agent import CodingAgent
from ..agents.qa_agent import KnowledgeQA_Agent

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
    current_parsed_input: Optional[ParsedInput] = None
    current_original_language: Optional[str] = None

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

        # Register agents after ensuring self.sub_agents exists (due to default_factory)
        self.register_agent(CodingAgent())
        self.register_agent(KnowledgeQA_Agent())

        # Initialize LLM client for the dispatcher's model
        self._initialize_llm_client(self.model)

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

            # Extract the suggested agent name from the response
            if hasattr(response, 'text') and response.text:
                raw_text = response.text.strip()
                # Simple check if the LLM returned a valid agent name from the list
                if raw_text and raw_text in self.sub_agents:
                    delegated_agent_name = raw_text
                    logger.info(f"LLM suggested delegation to: {delegated_agent_name}")
                elif raw_text and raw_text != "NO_AGENT":
                    logger.warning(f"LLM suggested agent '{raw_text}' but it's not registered or invalid.")
                    # Keep delegated_agent_name as "NO_AGENT"
                else: # Handles "NO_AGENT" or empty response
                    logger.info("LLM suggested no suitable internal agent (NO_AGENT or empty response).")
                    # Keep delegated_agent_name as "NO_AGENT"
            else:
                logger.warning(f"Unexpected delegation LLM response: No text attribute or empty text. Type: {type(response)}, Response: {response}")
                # Keep delegated_agent_name as "NO_AGENT"

        except AttributeError as ae:
             # genai.Client() 구조 관련 오류 가능성 (예: aio.models 경로)
             # 수정된 호출 방식에 대한 오류 처리 업데이트 필요
             logger.error(f"AttributeError during dispatcher LLM call (using aio.models.generate_content): {ae}")
             import traceback
             traceback.print_exc() # Print stack trace for debugging
             return "Error: Internal error during LLM call for delegation."
        except Exception as e:
            logger.error(f"Exception during dispatcher LLM call: {e}")
            import traceback
            traceback.print_exc() # Print stack trace for debugging
            return "Error: Exception during LLM call for delegation."

        # --- 3.3.3: A2A Dynamic Discovery Logic ---
        if delegated_agent_name == "NO_AGENT":
            logger.info("No suitable internal agent found via LLM. Attempting A2A Discovery (Placeholder).")
            # --- Placeholder Logic Start (Keep comments for future implementation) ---
            # 1. Construct A2A Discovery Query (based on parsed_input.intent, entities, domain, etc.)
            #    query_capabilities = [parsed_input.intent, parsed_input.domain] # Example
            #    logger.debug(f"Constructing A2A discovery query with capabilities: {query_capabilities}")

            # 2. Call Agent Hub Client's discovery method
            #    try:
            #        # agent_hub_client = self.get_agent_hub_client() # Needs implementation
            #        # discovered_agents = await agent_hub_client.discover(capabilities=query_capabilities)
            #        discovered_agents = [] # Placeholder: Assume no agents found for now
            #        logger.info(f"A2A Discovery Result (Placeholder): Found {len(discovered_agents)} agents.")
            #    except Exception as hub_error:
            #        logger.error(f"Error during A2A Discovery (Placeholder): {hub_error}")
            #        discovered_agents = []

            # 3. Evaluate discovered agents (Agent Cards) and select the best one
            #    selected_a2a_agent = None
            #    if discovered_agents:
            #        # Evaluation logic based on agent cards, cost, reliability etc.
            #        # selected_a2a_agent = discovered_agents[0] # Placeholder: select the first one
            #        logger.info(f"Selected A2A Agent (Placeholder): {selected_a2a_agent}")
            #        pass # Assign to delegated_agent_name or handle differently

            # 4. If an A2A agent is selected, prepare for A2A call (details in step 7)
            #    if selected_a2a_agent:
            #         # This might involve returning specific instructions or metadata
            #         # for the runner to initiate the A2A call.
            #         # For now, just log it.
            #         logger.info(f"Would initiate A2A call to {selected_a2a_agent} (Placeholder).")
            #         # return f"Delegating task via A2A to: {selected_a2a_agent.name}" # Example A2A return
            # --- Placeholder Logic End ---

            # For now, since A2A is just a placeholder, we proceed as if no external agent was found.
            # The final return statement handles the "NO_AGENT" case correctly.
            pass

        # 4. Return result (delegated agent name or indication of no delegation)
        # In a real scenario, the Runner would use this name to invoke the actual agent.
        # Here, we just return a message indicating the decision.

        # --- Design Note for Step 3.4: Context/Tool Injection by Runner --- #
        # The actual invocation of the delegated agent (if name != \"NO_AGENT\")
        # is handled by the ADK Runner outside this `process_request` method.
        # The Runner would need to:
        # 1. Get the selected agent instance using the `delegated_agent_name` from self.sub_agents.
        # 2. Prepare the invocation context for the selected agent:
        #    - Pass the relevant input, likely `self.current_parsed_input.english_text`.
        #    - Include necessary context like `self.current_original_language` and potentially conversation history (via SessionService).
        #    - Inject required tools (e.g., code executor for CodingAgent, web search for QA_Agent).
        #      Tools might need configuration like API keys, which the Runner or a config manager should provide.
        #    - The `InvocationContext` object is the standard way to pass this data.
        # 3. Call the selected agent's `invoke` or `run_async` method with the prepared context.
        # --- End Design Note ---

        if delegated_agent_name != "NO_AGENT":
            return f"Delegating task to agent: {delegated_agent_name}"
        else:
            # This message is returned if internal LLM said NO_AGENT *and* A2A placeholder didn't find one
            return "No suitable internal or external agent found to handle the request."

    # BaseAgent에는 invoke 또는 _run_async_impl 이 필요함
    # 기본 구현 또는 에러 발생시키도록 추가
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

# Type alias 등은 BaseAgent와 호환되도록 확인/수정 필요 (현재 코드에서는 직접 사용 안함) 