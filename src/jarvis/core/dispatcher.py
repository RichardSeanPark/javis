"""
중앙 디스패처 및 라우팅 로직
"""

import logging
import os
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import dotenv
import google.genai as genai
import httpx
from google.adk.agents import BaseAgent as Agent
from google.adk.agents import LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools import BaseTool
from google.genai.types import Content, GenerateContentResponse, Part
from pydantic import Field
from typing_extensions import TypedDict, override

# Attempt to import common types, handle potential ImportError if structure changes
try:
    from common.types import Task, TaskState, TaskStatus
except ImportError:
    logger.warning("Could not import common.types. A2A functionality might be affected.")
    # Define dummy types if needed, or let subsequent errors occur naturally
    Task = TaskState = TaskStatus = None

from ..agents.coding_agent import CodingAgent
from ..agents.qa_agent import KnowledgeQA_Agent
from ..components.input_parser import InputParserAgent
from ..components.response_generator import ResponseGenerator
from ..core.context_manager import ContextManager
from ..models.input import ParsedInput
from ..tools import (code_execution_tool, translate_tool, web_search_tool)

logger = logging.getLogger(__name__)
dotenv.load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        logger.info("Successfully configured genai with API key.")
    except AttributeError:
        logger.warning(
            "genai.configure does not exist. "
            "Relying on Client() to pick up credentials from environment."
        )
    except Exception as e:
        logger.error(f"Error configuring genai with API key: {e}")
else:
    logger.warning(
        "GEMINI_API_KEY not found in environment variables. "
        "LLM client initialization might fail."
    )

DEFAULT_MODEL_NAME = os.getenv("VERTEX_MODEL_NAME", "gemini-2.0-flash")
DEFAULT_INSTRUCTION = (
    "You are the central dispatcher for the Jarvis AI Framework. "
    "Your primary role is to understand the user's request (provided as input) "
    "and delegate it to the most suitable specialized agent available in your tools. "
    "Examine the descriptions of the available agents (tools) to make the best routing decision. "
    "Provide ONLY the name of the single best agent to delegate to, or 'NO_AGENT' "
    "if none are suitable. Do not add any explanation.\n\nAvailable Agents:\n"
)
AGENT_HUB_DISCOVER_URL = os.getenv("AGENT_HUB_DISCOVER_URL", "http://localhost:8001/discover")


class DelegationInfo(TypedDict):
    """Information needed to delegate a task to a sub-agent."""

    agent_name: str
    input_text: str
    original_language: Optional[str]
    required_tools: List[BaseTool]
    conversation_history: Optional[str]


class JarvisDispatcher(LlmAgent):
    """
    Central dispatcher for the Jarvis AI Framework.
    Analyzes requests and routes them to the appropriate specialized agent.
    """

    model: str = Field(default=DEFAULT_MODEL_NAME)
    input_parser: InputParserAgent = Field(default_factory=InputParserAgent)
    sub_agents: Dict[str, Agent] = Field(default_factory=dict)
    response_generator: ResponseGenerator = Field(default_factory=ResponseGenerator)
    llm_clients: Dict[str, Any] = Field(default_factory=dict, exclude=True)
    agent_tool_map: Dict[str, List[BaseTool]] = Field(default_factory=dict)
    current_parsed_input: Optional[ParsedInput] = None
    current_original_language: Optional[str] = None
    http_client: httpx.AsyncClient = Field(default=None, exclude=True)
    context_manager: ContextManager = Field(default_factory=ContextManager)

    def __init__(self, **kwargs):
        """Initializes the JarvisDispatcher."""
        kwargs.setdefault("name", "JarvisDispatcher")
        kwargs.setdefault(
            "description",
            "Central dispatcher for Jarvis AI Framework. Routes to specialized agents.",
        )
        super().__init__(**kwargs)

        if "model" not in kwargs:
            self.model = DEFAULT_MODEL_NAME
            logger.info(f"Dispatcher model default: {self.model}")
        # Ensure instruction is set
        self.instruction = DEFAULT_INSTRUCTION

        # Define the tool map *before* registering agents that might use it
        self.agent_tool_map = {
            "CodingAgent": [code_execution_tool],
            "KnowledgeQA_Agent": [web_search_tool, translate_tool],
        }

        # Register initial agents
        self.register_agent(CodingAgent())
        self.register_agent(KnowledgeQA_Agent())

        # Initialize LLM client for the dispatcher itself
        self._initialize_llm_client(self.model)

        # Initialize HTTP client for A2A calls
        # Use a shared client instance for potential connection pooling
        self.http_client = httpx.AsyncClient()
        logger.info("Initialized httpx.AsyncClient.")
        logger.info(f"Initialized JarvisDispatcher: {self.name}")

    def _initialize_llm_client(self, model_name: str):
        """Initializes LLM client for a given model name if not already done."""
        if not model_name or "mock-model" in model_name:
            return
        if model_name not in self.llm_clients:
            if not API_KEY:
                logger.error(f"No API key for {model_name}. Cannot init LLM client.")
                self.llm_clients[model_name] = None
                return
            try:
                self.llm_clients[model_name] = genai.Client(api_key=API_KEY)
                logger.info(f"LLM client initialized for {model_name}")
            except Exception as e:
                logger.error(f"LLM client init failed for {model_name}: {e}")
                self.llm_clients[model_name] = None

    def get_llm_client(self, model_name: str) -> Optional[Any]:
        """Retrieves the LLM client for the given model name, initializing if needed."""
        if model_name not in self.llm_clients:
            logger.warning(f"LLM '{model_name}' not pre-initialized. Attempting init.")
            self._initialize_llm_client(model_name)
        client = self.llm_clients.get(model_name)
        if client is None:
            logger.error(f"LLM client for '{model_name}' is unavailable.")
        return client

    def register_agent(self, agent: Agent):
        """Registers a sub-agent with the dispatcher."""
        if not isinstance(agent, Agent):
            raise TypeError("Registered agent must be an instance of Agent subclass.")
        if not agent.name:
            raise ValueError("Registered agent must have a name.")

        # Initialize LLM client for the agent if it's an LlmAgent with a model
        if isinstance(agent, LlmAgent) and agent.model:
            self._initialize_llm_client(agent.model)

        is_overwriting = agent.name in self.sub_agents
        self.sub_agents[agent.name] = agent

        # Update the dispatcher's tools list (used for LLM delegation prompt)
        self.tools = list(self.sub_agents.values())

        log_msg = (
            f"Agent '{agent.name}' overwritten." if is_overwriting else f"Agent '{agent.name}' registered."
        )
        logger.info(log_msg)

    async def process_request(
        self, user_input: str, session_id: Optional[str] = None
    ) -> Union[DelegationInfo, str]:
        """
        Parses user input and determines the appropriate agent or action.

        Returns:
            DelegationInfo if an internal agent is selected, or a string response
            (error message, A2A result, or fallback message).
        """
        try:
            # 1. Parse Input
            if not self.input_parser:
                logger.error("Input parser unavailable.")
                return "Error: Input parser unavailable."
            try:
                parsed_input = await self.input_parser.process_input(user_input)
            except Exception as e:
                logger.error(f"Input parsing error: {e}", exc_info=True)
                return "Error: Failed to parse input."

            self.current_parsed_input = parsed_input
            self.current_original_language = (
                parsed_input.original_language if parsed_input else None
            )

            if not self.current_parsed_input:
                logger.error("Input parsing yielded no result.")
                return "Error: Input parsing failed."

            llm_input_text = self.current_parsed_input.english_text
            logger.info(f"Dispatcher deciding for: {llm_input_text[:100]}...")

            # --- Get Conversation History ---
            conversation_history = None
            if session_id:
                try:
                    conversation_history = (
                        self.context_manager.get_formatted_context(session_id)
                    )
                    logger.debug(f"Got history for session {session_id}")
                except Exception as e:
                    logger.error(
                        f"Error getting history for session {session_id}: {e}",
                        exc_info=True,
                    )
            else:
                logger.warning("No session_id provided, cannot get history.")
            # --- End Get History ---

            # 2. Prepare Prompt for Delegation LLM
            try:
                tool_descs = "\n".join([
                    f"- {tool.name}: {tool.description}"
                    for tool in self.tools
                    if hasattr(tool, 'name') and hasattr(tool, 'description')
                ])
                prompt = f"{self.instruction}\n{tool_descs}\n\nUser Request: {llm_input_text}"
                logger.debug(f"Dispatcher Prompt:\n{prompt}")
            except Exception as e:
                logger.error(f"Error preparing dispatcher prompt: {e}", exc_info=True)
                return "Error: Internal error preparing request."

            # 3. Call LLM for Delegation Decision / A2A Check
            dispatcher_llm_client = self.get_llm_client(self.model)
            if not dispatcher_llm_client:
                logger.error(f"Dispatcher LLM client ({self.model}) unavailable.")
                return "Error: Dispatcher LLM unavailable."

            delegated_agent_name = "NO_AGENT"
            try:
                logger.info(f"Calling dispatcher LLM ({self.model}) for delegation.")
                response = await dispatcher_llm_client.aio.models.generate_content(
                    model=self.model, contents=[Content(parts=[Part(text=prompt)])]
                )
                logger.debug(f"Raw Delegation LLM Response: {response}")

                if response and hasattr(response, "text"):
                    potential_agent_name = response.text.strip()
                    if potential_agent_name in self.sub_agents:
                        delegated_agent_name = potential_agent_name
                        logger.info(f"LLM decided delegation to: {delegated_agent_name}")
                    elif potential_agent_name == "NO_AGENT":
                        logger.info("LLM -> NO_AGENT. Checking A2A...")
                        # Try A2A Discovery and Call
                        try:
                            capability_query = llm_input_text  # Fallback
                            if self.current_parsed_input.intent:
                                capability_query = f"Handle intent '{self.current_parsed_input.intent}' for query: {llm_input_text}"
                                if self.current_parsed_input.domain:
                                    capability_query = f"Handle intent '{self.current_parsed_input.intent}' in domain '{self.current_parsed_input.domain}' for query: {llm_input_text}"

                            logger.info(f"Discovering A2A agents for: {capability_query[:100]}...")
                            discovered_agents = await self._discover_a2a_agents(capability_query)

                            if discovered_agents:
                                logger.info(f"Found {len(discovered_agents)} A2A agents. Calling first.")
                                selected_a2a_agent_card = discovered_agents[0]
                                agent_name_to_call = selected_a2a_agent_card.get("name", "Unknown A2A")
                                logger.info(f"Attempting A2A call to: {agent_name_to_call}")
                                a2a_result = await self._call_a2a_agent(selected_a2a_agent_card, llm_input_text)
                                # If A2A call is successful, return its result directly
                                return a2a_result
                            else:
                                logger.info("No suitable A2A agents discovered.")
                                # delegated_agent_name remains NO_AGENT
                        except Exception as a2a_e:
                            logger.error(f"Error during A2A discovery/call: {a2a_e}", exc_info=True)
                            # delegated_agent_name remains NO_AGENT
                    else:
                        logger.warning(f"LLM returned unknown agent name: '{potential_agent_name}'. Treating as NO_AGENT.")
                        # delegated_agent_name remains NO_AGENT
                else:
                    logger.error(f"Failed to get valid text response from delegation LLM: {response}")
                    # delegated_agent_name remains NO_AGENT

            except Exception as llm_e:
                logger.error(f"Error during LLM delegation call or A2A check: {llm_e}", exc_info=True)
                # Fall through to fallback message if LLM/A2A fails

            # 4. Prepare Return Value (DelegationInfo or Fallback Message)
            if delegated_agent_name != "NO_AGENT" and delegated_agent_name in self.sub_agents:
                # Prepare DelegationInfo for internal agent
                try:
                    required_tools = self.agent_tool_map.get(delegated_agent_name, [])
                    logger.info(f"Preparing DelegationInfo for {delegated_agent_name}")
                    # Use dictionary constructor directly for clarity
                    delegation_info: DelegationInfo = {
                        "agent_name": delegated_agent_name,
                        "input_text": llm_input_text,
                        "original_language": self.current_original_language,
                        "required_tools": required_tools,
                        "conversation_history": conversation_history,
                    }
                    return delegation_info
                except Exception as prep_e:
                    logger.error(f"Error preparing DelegationInfo for {delegated_agent_name}: {prep_e}", exc_info=True)
                    return f"Error: Internal error preparing delegation for {delegated_agent_name}."
            else:
                # Fallback message if no internal or A2A agent handled it
                logger.info("No suitable internal or A2A agent could handle the request.")
                return "I cannot find a suitable agent to handle your request at this time."

        except Exception as outer_e:
            # Catch-all for the entire process_request method
            logger.error(f"Unexpected error in process_request: {outer_e}", exc_info=True)
            return "Error: An unexpected internal error occurred."

    @override
    async def invoke(self, ctx: InvocationContext):
        """Direct invocation is not supported for the dispatcher."""
        raise NotImplementedError(
            "JarvisDispatcher should not be invoked directly. Use run via Runner."
        )

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Handles the execution flow when run via ADK Runner.
        Calls process_request and yields delegation or final response events.
        """
        user_input: Optional[str] = None
        session_id = ctx.session.id if ctx.session else None
        # Default error message if something goes wrong before response generation
        final_response: str = "Error: An unexpected error occurred."
        sub_agent_to_restore: Optional[Agent] = None # Track agent for finally block
        original_tools: Optional[List[BaseTool]] = None
        original_instruction: Optional[str] = None

        try:
            # Extract user input from context
            if ctx.user_content and ctx.user_content.parts:
                user_input = ctx.user_content.parts[0].text

            if not user_input:
                logger.warning("_run_async_impl called without user input.")
                final_response = "Error: Could not get user input from context."
            else:
                # Process the request to decide action
                result = await self.process_request(user_input, session_id=session_id)

                if isinstance(result, dict) and "agent_name" in result:
                    # Case 1: Delegate to an internal sub-agent
                    delegation_info: DelegationInfo = result
                    agent_name = delegation_info["agent_name"]

                    # Get the sub-agent instance - raise error if not found
                    if agent_name not in self.sub_agents:
                        logger.error(f"Delegation target agent '{agent_name}' not found.")
                        final_response = f"Error: Agent '{agent_name}' not found."
                        # Go directly to final response generation
                    else:
                        sub_agent = self.sub_agents[agent_name]
                        sub_agent_to_restore = sub_agent # Store for finally block
                        logger.info(f"Dispatcher signalling delegation to: {agent_name}")
                        
                        # Store original state *before* modification
                        original_tools = sub_agent.tools
                        original_instruction = getattr(sub_agent, "instruction", None)

                        # --- Temporarily modify sub-agent --- #
                        sub_agent.tools = delegation_info["required_tools"]
                        logger.debug(f"Temp set tools for {agent_name}")

                        context_prompt = "\n\n---\nContext:\n"
                        if delegation_info["conversation_history"]:
                            context_prompt += f'History:\n{delegation_info["conversation_history"]}\n'
                        if delegation_info["original_language"]:
                            context_prompt += f'Original Language: {delegation_info["original_language"]}\n'
                        context_prompt += "---"

                        base_instruction = original_instruction or ""
                        temp_instruction = base_instruction + context_prompt

                        if hasattr(sub_agent, "instruction"):
                            setattr(sub_agent, "instruction", temp_instruction)
                            logger.debug(f"Temp updated instruction for {agent_name}")
                        else:
                            logger.warning(f"Agent {agent_name} lacks 'instruction' attribute.")
                        # --- End temporary modification --- #

                        # Yield the delegation event - Runner handles the actual call
                        yield Event(
                            author=self.name,
                            content=Content(parts=[Part(text=f"[System] Delegating task to {agent_name}. Runner will invoke.")])
                        )
                        # After yielding delegation, this function's work is done.
                        # The finally block below will restore the agent.
                        return # EXIT here after yielding delegation

                elif isinstance(result, str):
                    # Case 2: process_request returned a direct response string
                    # (Error, A2A result, fallback message)
                    final_response = result
                    logger.info(f"Using direct response from process_request: {final_response[:100]}...")
                else:
                    # Should not happen if process_request is correct
                    logger.error(f"Unexpected result type from process_request: {type(result)}")
                    final_response = "Error: Unexpected internal dispatcher state."

            # If we reach here, it means no delegation event was yielded.
            # Yield the final response (could be success or error message).
            logger.info(f"Generating final response (orig lang: {self.current_original_language})")
            generated_response = await self.response_generator.generate_response(
                english_result=final_response,  # Pass the determined response/error
                original_language=self.current_original_language,
            )
            yield Event(author=self.name, content=Content(parts=[Part(text=generated_response)]))
            logger.info("Final response event yielded.")

        except Exception as run_e:
            # Catch-all for errors within _run_async_impl itself
            logger.error(f"Unexpected error in _run_async_impl: {run_e}", exc_info=True)
            # Try to yield a generic error response
            try:
                error_response = await self.response_generator.generate_response(
                    english_result="Error: An unexpected error occurred during processing.",
                    original_language=self.current_original_language
                )
                yield Event(author=self.name, content=Content(parts=[Part(text=error_response)]))
            except Exception as gen_e_inner:
                # If even response generation fails, yield a very basic error
                logger.error(f"Error generating fallback error response: {gen_e_inner}")
                yield Event(author=self.name, content=Content(parts=[Part(text="Error: Critical failure.")]))
        finally:
            # --- Restore sub-agent state if it was modified --- #
            if sub_agent_to_restore:
                logger.debug(f"Executing finally block for {sub_agent_to_restore.name}")
                # Check if original values were captured before trying to restore
                if original_tools is not None:
                    sub_agent_to_restore.tools = original_tools
                    logger.debug(f"Restored tools for {sub_agent_to_restore.name}")
                if hasattr(sub_agent_to_restore, "instruction") and original_instruction is not None:
                    setattr(sub_agent_to_restore, "instruction", original_instruction)
                    logger.debug(f"Restored instruction for {sub_agent_to_restore.name}")
            # --- End restoration --- #

    async def _discover_a2a_agents(self, capability: str) -> List[Dict[str, Any]]:
        """Discovers A2A agents from the Agent Hub based on capability."""
        logger.info(f"Discovering A2A agents for: {capability[:100]}...")
        try:
            # Use the shared http_client instance
            response = await self.http_client.post(
                AGENT_HUB_DISCOVER_URL,
                json={"required_capabilities": [capability]},
                timeout=10.0 # Add a timeout
            )
            response.raise_for_status()
            data = response.json()
            discovered_agents = data.get("discovered_agents", [])
            logger.info(f"A2A Discovery found {len(discovered_agents)} agents.")
            return discovered_agents
        except httpx.RequestError as e:
            logger.error(f"A2A Discovery failed (network error): {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"A2A Discovery failed (status {e.response.status_code}): {e.response.text}")
        except Exception as e:
            logger.error(f"A2A Discovery failed (unexpected error): {e}", exc_info=True)
        return [] # Return empty list on any error

    async def _call_a2a_agent(self, agent_card: Dict[str, Any], task_input: Any) -> str:
        """Calls an A2A agent based on its Agent Card."""
        a2a_endpoint = agent_card.get("a2a_endpoint")
        agent_name = agent_card.get("name", "Unknown A2A Agent")

        if not a2a_endpoint:
            msg = f"Cannot call A2A agent '{agent_name}': Missing 'a2a_endpoint'."
            logger.error(msg)
            return f"Error: Configuration missing for {agent_name}."
            
        # Ensure Task types are available (check done at import time)
        if not Task or not TaskState or not TaskStatus:
             msg = "A2A Task types not loaded. Cannot call A2A agent."
             logger.error(msg)
             return f"Error: {msg}"

        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            issuer=self.name,
            audience=agent_name,
            scopes=["execute"],
            input=[Part(text=str(task_input))],  # Ensure input is a text Part
            status=TaskStatus(state=TaskState.PENDING),
        )

        logger.info(f"Sending task {task_id} to A2A agent {agent_name} at {a2a_endpoint}")
        try:
            # Use the shared http_client instance
            response = await self.http_client.post(
                a2a_endpoint,
                json=task.model_dump(mode="json"), # Use model_dump
                timeout=30.0 # Add a longer timeout for agent execution
            )
            response.raise_for_status()
            result_task_data = response.json()
            result_task = Task(**result_task_data)

            if result_task.status.state == TaskState.COMPLETED:
                # Extract text result from artifacts
                text_result = " ".join([
                    part.text for part in result_task.artifacts if hasattr(part, "text")
                ])
                if text_result:
                    logger.info(f"A2A Task {task_id} completed by {agent_name}.")
                    return text_result
                else:
                    logger.warning(f"A2A Task {task_id} completed by {agent_name} but no text artifact found.")
                    return f"A2A agent {agent_name} completed but returned no text result."
            else:
                error_msg = result_task.status.error or "unknown error"
                logger.error(f"A2A Task {task_id} failed for {agent_name}. State: {result_task.status.state}, Error: {error_msg}")
                return f"Error from A2A agent {agent_name}: {error_msg}"

        except httpx.RequestError as e:
            logger.error(f"Failed to send task to {agent_name} (network error): {e}")
            return f"Error: Could not reach A2A agent {agent_name}."
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to call {agent_name} (status {e.response.status_code}): {e.response.text}")
            return f"Error: Received error status from A2A agent {agent_name}."
        except Exception as e:
            logger.error(f"Failed to call {agent_name} (unexpected error): {e}", exc_info=True)
            return f"Error: Unexpected error calling A2A agent {agent_name}."

    # Ensure the HTTP client is closed when the dispatcher is no longer needed
    # This might require integration with the application lifecycle (e.g., FastAPI lifespan)
    # For now, add a simple close method. Proper cleanup might need a different approach.
    async def close_http_client(self):
        if self.http_client:
             await self.http_client.aclose()
             logger.info("Closed httpx.AsyncClient.") 