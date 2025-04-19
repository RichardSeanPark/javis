"""
중앙 디스패처 및 라우팅 로직
"""

from google.adk.agents import LlmAgent, BaseAgent as Agent
# from google.adk.models import LlmConfig # 더 이상 사용되지 않음
from ..components.input_parser import InputParserAgent
from ..components.response_generator import ResponseGenerator # Import ResponseGenerator
# from ..core.context_manager import ContextManager # Import ContextManager - 주석 처리
from pydantic import Field # Field 임포트 추가
from ..models.input import ParsedInput # ParsedInput 임포트 추가
from typing import Optional, List, Dict, Any, AsyncGenerator, TypedDict, Union # Import List, Any, AsyncGenerator, TypedDict, Union
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

from ..core.context_manager import ContextManager # ContextManager 임포트

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

class DelegationInfo(TypedDict):
    """하위 에이전트 호출에 필요한 정보를 담는 타입 딕셔너리"""
    agent_name: str
    input_text: str
    original_language: Optional[str]
    required_tools: List[BaseTool]
    conversation_history: Optional[str] # 추가: 대화 이력

class JarvisDispatcher(LlmAgent):
    """
    Central dispatcher for the Jarvis AI Framework.
    Analyzes requests and routes them to the appropriate specialized agent.
    """
    # Declare fields using Pydantic Field
    model: str = Field(default=DEFAULT_MODEL_NAME) # Explicitly declare model field
    input_parser: InputParserAgent = Field(default_factory=InputParserAgent)
    sub_agents: Dict[str, Agent] = Field(default_factory=dict)
    response_generator: ResponseGenerator = Field(default_factory=ResponseGenerator) # Add response_generator field
    # context_manager: ContextManager = Field(default_factory=ContextManager) # 주석 처리
    llm_clients: Dict[str, Any] = Field(default_factory=dict, exclude=True)
    agent_tool_map: Dict[str, List[BaseTool]] = Field(default_factory=dict) # Added agent_tool_map
    current_parsed_input: Optional[ParsedInput] = None
    current_original_language: Optional[str] = None
    http_client: httpx.AsyncClient = Field(default=None, exclude=True) # HTTP 클라이언트 필드 추가
    context_manager: ContextManager = Field(default_factory=ContextManager) # ContextManager 추가

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
            logger.warning(f"Agent with name '{agent.name}' overwritten.")
        logger.info(f"Agent '{agent.name}' (type: {type(agent)}, model: {getattr(agent, 'model', 'N/A')}) registered/updated. Current tools: {[getattr(t, 'name', 'N/A') for t in self.tools]}")

    async def process_request(self, user_input: str, session_id: Optional[str] = None) -> Union[DelegationInfo, str]:
        """
        사용자 입력을 받아 파싱하고, 위임할 에이전트 및 관련 정보를 결정합니다.
        반환값: 위임이 필요하면 DelegationInfo, 아니면 에러 또는 정보 메시지 문자열.
        session_id 추가.
        """
        try:
            # 1. Parse Input
            if not self.input_parser:
                logger.error("Input parser not initialized!")
                return "Error: Input parser not available."
            try:
                parsed_input = await self.input_parser.process_input(user_input)
            except Exception as e:
                logger.error(f"Error during input parsing: {e}", exc_info=True)
                return "Error: Failed to parse your input."

            if not parsed_input:
                logger.error("Input parsing returned None or empty. Cannot proceed.")
                return "Error: Input parsing failed to produce results."

            self.current_parsed_input = parsed_input
            self.current_original_language = parsed_input.original_language
            llm_input_text = parsed_input.english_text
            logger.info(f"Dispatcher deciding delegation for: {llm_input_text[:100]}...")

            # --- Get Conversation History ---
            conversation_history = None
            if session_id:
                try:
                    conversation_history = self.context_manager.get_formatted_context(session_id)
                    logger.debug(f"Retrieved conversation history for session {session_id}:\n{conversation_history[:200]}...")
                except Exception as e:
                    logger.error(f"Error retrieving conversation history for session {session_id}: {e}", exc_info=True)
                    # Proceed without history if context retrieval fails
            else:
                logger.warning("No session_id provided to process_request, cannot retrieve conversation history.")
            # --- End Get History ---

            # 2. Prepare Prompt
            try:
                tool_descriptions = "\n".join([
                    f"- {getattr(tool, 'name', 'N/A')}: {getattr(tool, 'description', 'N/A')}"
                    for tool in self.tools
                ])
                prompt = f"{self.instruction}\n{tool_descriptions}\n\nUser Request: {llm_input_text}"
                logger.debug(f"Dispatcher Prompt:\n{prompt}")
            except Exception as e:
                logger.error(f"Error preparing dispatcher prompt: {e}", exc_info=True)
                return "Error: Internal error preparing request."

            # 3. Call LLM for Delegation
            dispatcher_llm_client = self.get_llm_client(self.model)
            if not dispatcher_llm_client:
                logger.error(f"LLM client for dispatcher (model key: {self.model}) not initialized!")
                return "Error: LLM client not available for dispatcher."

            delegated_agent_name = "NO_AGENT"
            try:
                logger.info(f"Calling dispatcher's LLM (model={self.model}) via Client for delegation decision.")
                response = await dispatcher_llm_client.aio.models.generate_content(
                    model=self.model,
                    contents=[Content(parts=[Part(text=prompt)])]
                )
                logger.debug(f"Raw Delegation LLM Response type: {type(response)}")
                logger.debug(f"Raw Delegation LLM Response: {response}")

                if response and hasattr(response, 'text'):
                    potential_agent_name = response.text.strip()
                    if potential_agent_name in self.sub_agents:
                        delegated_agent_name = potential_agent_name
                        logger.info(f"Dispatcher LLM decided to delegate to internal agent: {delegated_agent_name}")
                    elif potential_agent_name == "NO_AGENT":
                        logger.info("Dispatcher LLM indicated no suitable internal agent found. Checking A2A...")
                        try:
                            # Ensure intent and domain exist before using them
                            intent = getattr(self.current_parsed_input, 'intent', 'unknown')
                            domain = getattr(self.current_parsed_input, 'domain', 'unknown')
                            needed_capability = f"Handle intent '{intent}' in domain '{domain}'"
                            discovered_agents = await self._discover_a2a_agents(needed_capability)

                            if discovered_agents:
                                logger.info(f"Discovered {len(discovered_agents)} potential A2A agents. Selecting the first one.")
                                selected_a2a_agent_card = discovered_agents[0]
                                agent_name_to_call = selected_a2a_agent_card.get('name', 'Unknown A2A Agent')
                                logger.info(f"Attempting to call A2A agent: {agent_name_to_call}")
                                a2a_result = await self._call_a2a_agent(selected_a2a_agent_card, llm_input_text)
                                return a2a_result # Return A2A result directly
                            else:
                                logger.info("No suitable A2A agents discovered.")
                                delegated_agent_name = "NO_AGENT" # Explicitly set NO_AGENT
                        except Exception as a2a_e:
                            logger.error(f"Error during A2A discovery or call process: {a2a_e}", exc_info=True)
                            delegated_agent_name = "NO_AGENT" # If A2A fails, fall back
                    else:
                        logger.warning(f"Dispatcher LLM returned an unknown agent name: '{potential_agent_name}'. Treating as NO_AGENT.")
                        delegated_agent_name = "NO_AGENT"
                else:
                    logger.error(f"Failed to get valid text response from delegation LLM. Response: {response}")
                    delegated_agent_name = "NO_AGENT"
            except Exception as llm_e:
                logger.error(f"Error during LLM delegation call: {llm_e}", exc_info=True)
                delegated_agent_name = "NO_AGENT" # If LLM fails, consider it NO_AGENT

            # 4. Return Result (Internal Delegation or Fallback)
            if delegated_agent_name != "NO_AGENT" and delegated_agent_name in self.sub_agents:
                try:
                    required_tools = self.agent_tool_map.get(delegated_agent_name, [])
                    logger.info(f"Preparing delegation info for internal agent '{delegated_agent_name}' with tools: {[getattr(t, 'name', 'Unnamed Tool') for t in required_tools]}")
                    delegation_info: DelegationInfo = {
                        "agent_name": delegated_agent_name,
                        "input_text": llm_input_text,
                        "original_language": self.current_original_language,
                        "required_tools": required_tools,
                        "conversation_history": conversation_history
                    }
                    return delegation_info
                except Exception as prep_e:
                    logger.error(f"Error preparing DelegationInfo for {delegated_agent_name}: {prep_e}", exc_info=True)
                    # Return specific error if preparing delegation info fails
                    return f"Error: Internal error preparing delegation for agent {delegated_agent_name}."
            else:
                # Fallback if no internal agent and A2A failed/not found/LLM failed
                logger.info("No suitable internal or A2A agent could handle the request.")
                return "I cannot find a suitable agent to handle your request at this time."

        except Exception as outer_e:
            # Catch-all for the entire method
            logger.error(f"Unexpected error in process_request: {outer_e}", exc_info=True)
            return "Error: An unexpected internal error occurred while processing your request."

    @override
    async def invoke(self, ctx: InvocationContext):
        raise NotImplementedError("JarvisDispatcher should not be invoked directly. Use process_request or run via Runner.")

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Runner로부터 호출받아 process_request 실행 후,
        하위 에이전트 호출 위임 또는 최종 메시지 반환.
        Adds error handling.
        """
        user_input = None
        session_id = ctx.session.id if ctx.session else None
        final_response_message = "Error: An unexpected error occurred." # Default error message
        original_tools = None
        original_instruction = None
        sub_agent_to_restore = None # Use a different variable to track which agent needs restoration

        try:
            # Extract user input
            if ctx.user_content and hasattr(ctx.user_content, 'parts') and ctx.user_content.parts:
                if hasattr(ctx.user_content.parts[0], 'text'):
                    user_input = ctx.user_content.parts[0].text

            if not user_input:
                logger.warning("_run_async_impl called without user input text in context.")
                final_response_message = "Error: Could not get user input from context."
            else:
                # Process the request to get delegation info or a direct response string
                result = await self.process_request(user_input, session_id=session_id)

                if isinstance(result, dict) and "agent_name" in result:
                    # --- Handle Delegation ---
                    delegation_info: DelegationInfo = result
                    agent_name = delegation_info["agent_name"]

                    if agent_name not in self.sub_agents:
                        logger.error(f"Delegation target agent '{agent_name}' not found in sub_agents.")
                        final_response_message = f"Error: Could not find agent {agent_name} to delegate to."
                    else:
                        sub_agent = self.sub_agents[agent_name]
                        sub_agent_to_restore = sub_agent # Mark this agent for potential restoration
                        original_tools = sub_agent.tools
                        original_instruction = getattr(sub_agent, 'instruction', None)

                        try:
                            # Temporarily modify sub-agent for the call
                            logger.info(f"Dispatcher delegating to sub-agent: {agent_name}")
                            # --- Tool Injection Point ---
                            original_tools = sub_agent.tools # Store original tools
                            required_tools_from_info = delegation_info["required_tools"]
                            sub_agent.tools = required_tools_from_info
                            logger.debug(f"Temporarily injected tools into {agent_name}: {[getattr(t, 'name', 'Unnamed Tool') for t in sub_agent.tools]}")
                            # --- End Tool Injection ---

                            context_prompt = "\n\n---\nContext:\n"
                            if delegation_info["conversation_history"]:
                                context_prompt += f'Conversation History:\n{delegation_info["conversation_history"]}\n'
                            context_prompt += f'Original Language: {delegation_info["original_language"]}\n---'

                            base_instruction = original_instruction if original_instruction is not None else ""
                            temp_instruction = base_instruction + context_prompt

                            if hasattr(sub_agent, 'instruction'):
                                setattr(sub_agent, 'instruction', temp_instruction)
                                logger.debug(f"Temporarily updated instruction for {agent_name}")
                            else:
                                logger.warning(f"Agent {agent_name} does not have an 'instruction' attribute to update.")

                            # Yield the delegation event to the Runner
                            logger.info(f"Yielding delegation event for {agent_name} to Runner.")
                            yield Event(
                                author=self.name,
                                content=Content(parts=[Part(text=f"[System] Delegating to {agent_name}. Runner should invoke.")])
                            )
                            # If delegation event yields successfully, the generator finishes here.
                            # The runner will handle the actual sub-agent call.
                            logger.debug(f"Delegation event yielded for {agent_name}. Exiting _run_async_impl generator.")
                            return # Exit generator

                        except Exception as delegation_prep_error:
                             logger.error(f"Error during delegation prep or event yield for {agent_name}: {delegation_prep_error}", exc_info=True)
                             final_response_message = f"Error: Internal error while preparing delegation for agent {agent_name}."
                             # Fall through to finally block for cleanup, then yield error

                elif isinstance(result, str):
                    # --- Handle Direct Response from process_request (e.g., error, A2A result, fallback) ---
                    logger.info(f"Dispatcher's process_request returned direct response: {result[:100]}...")
                    final_response_message = result
                else:
                    # --- Handle Unexpected Result from process_request ---
                    logger.error(f"process_request returned unexpected type: {type(result)}")
                    final_response_message = "Error: Internal dispatcher error due to unexpected result type."

        except Exception as outer_e:
            # Catch any unexpected errors in the main try block
            logger.error(f"Unexpected error in _run_async_impl: {outer_e}", exc_info=True)
            final_response_message = "Error: An unexpected error occurred during execution." # Overwrite default error
        finally:
            # --- Restore Sub-Agent State ---
            # This block executes regardless of whether delegation happened or an error occurred within this generator's scope.
            # CRITICAL NOTE: This restoration happens when *this generator* finishes, which might be *before* the Runner invokes the sub-agent.
            # The effectiveness of the temporary tool injection relies on the Runner acting immediately on the yielded agent state.
            if sub_agent_to_restore:
                try:
                    # Check if original_tools was actually assigned before attempting restoration
                    if 'original_tools' in locals() and original_tools is not None:
                         logger.debug(f"Attempting to restore original tools for {sub_agent_to_restore.name}")
                         sub_agent_to_restore.tools = original_tools
                    else:
                         logger.warning(f"Cannot restore original tools for {sub_agent_to_restore.name}: 'original_tools' not defined in this scope (likely due to early exit or error before assignment).")

                    # Restore instruction similarly
                    if hasattr(sub_agent_to_restore, 'instruction'):
                        if 'original_instruction' in locals() and original_instruction is not None:
                            setattr(sub_agent_to_restore, 'instruction', original_instruction)
                            logger.debug(f"Restored original instruction for {sub_agent_to_restore.name}")
                        # else: # No warning needed if instruction wasn't modified
                except Exception as restore_e:
                     logger.error(f"Error restoring state for {sub_agent_to_restore.name}: {restore_e}", exc_info=True)
            # --- End Restore ---

        # --- Generate and Yield Final Response/Error Event ---
        # This section is reached ONLY IF:
        # 1. Delegation didn't happen (process_request returned string or error).
        # 2. An error occurred during the try block of _run_async_impl.
        final_ai_response_text = "Error: Failed to generate final response." # Fallback
        try:
            logger.info(f"Generating final response/error message: {final_response_message[:100]}...")
            processed_final_response = await self.response_generator.generate_response(
                final_response_message, self.current_original_language # Use the language set by process_request
            )
            final_ai_response_text = processed_final_response # Store the successfully generated response

            # --- Save context BEFORE yielding the final response ---
            if session_id and user_input:
                try:
                    self.context_manager.add_message(
                        session_id=session_id,
                        user_input=user_input, # Use the input extracted at the beginning
                        ai_response=final_ai_response_text,
                        original_language=self.current_original_language
                    )
                except Exception as cm_e:
                    logger.error(f"Failed to save context for session {session_id}: {cm_e}", exc_info=True)
            # --- End Save context ---

            yield Event(author=self.name, content=Content(parts=[Part(text=final_ai_response_text)]))
        except Exception as gen_e:
            logger.error(f"Error during final response generation: {gen_e}", exc_info=True)
            # Fallback to a very basic error message if response generator fails
            final_ai_response_text = "Error: Failed to generate final response."

            # --- Attempt to save context even on generation error ---
            if session_id and user_input:
                try:
                    self.context_manager.add_message(
                        session_id=session_id,
                        user_input=user_input,
                        ai_response=final_ai_response_text, # Save the error message as AI response
                        original_language=self.current_original_language
                    )
                except Exception as cm_e:
                    logger.error(f"Failed to save context (after generation error) for session {session_id}: {cm_e}", exc_info=True)
            # --- End Save context ---

            yield Event(author=self.name, content=Content(parts=[Part(text=final_ai_response_text)]))

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