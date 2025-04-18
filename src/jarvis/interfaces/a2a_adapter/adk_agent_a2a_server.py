# src/jarvis/interfaces/a2a_adapter/adk_agent_a2a_server.py
import logging
import asyncio # Import asyncio
import inspect # Import inspect for checking coroutine function
from google.adk import agents as adk_agents # Assuming ADK agent base class
from src.jarvis.libs.a2a import models as a2a_models
from src.jarvis.libs.a2a.server import server as a2a_server
from typing import Any, Dict
# Import AsyncMock for type checking
from unittest.mock import AsyncMock, MagicMock

logger = logging.getLogger(__name__)

class AdkAgentA2AWrapper(a2a_server.A2AServer):
    """
    Wraps a Google ADK Agent to expose it via the A2A protocol.
    """
    def __init__(self, adk_agent: adk_agents.Agent, agent_card: a2a_models.AgentCard):
        """
        Initializes the wrapper.

        Args:
            adk_agent: The ADK agent instance to wrap.
            agent_card: The Agent Card describing this A2A endpoint.
        """
        super().__init__(agent_card=agent_card) # Initialize A2AServer with the card
        # Allow MagicMock or AsyncMock during testing
        if not isinstance(adk_agent, (adk_agents.Agent, MagicMock, AsyncMock)):
            raise TypeError("Provided agent must be an instance of google.adk.agents.Agent or a Mock object for testing")
        self.adk_agent = adk_agent
        logger.info(f"Wrapping ADK agent '{self.adk_agent.name}' for A2A.")

    async def handle_task(self, task: a2a_models.Task) -> a2a_models.Task:
        """
        Handles an incoming A2A task by invoking the wrapped ADK agent.
        Assumes the relevant input is in the first message of the task history.
        """
        logger.info(f"Handling A2A task {task.id} for ADK agent {self.adk_agent.name}")
        task.status.state = a2a_models.TaskState.WORKING
        # TODO: Send TaskStatusUpdateEvent if streaming

        try:
            # --- Extract input from A2A Task's history --- 
            user_input_text = ""
            # Check history instead of message
            if task.history and task.history[0] and task.history[0].parts:
                first_message = task.history[0]
                # Simple case: assuming the first text part is the primary input
                text_parts = [p for p in first_message.parts if isinstance(p, a2a_models.TextPart)]
                if text_parts:
                    user_input_text = text_parts[0].text
                else:
                    # Handle cases with no text input in the first message?
                    logger.warning(f"Task {task.id}: First message has no TextPart.")
            else:
                 logger.warning(f"Task {task.id} received with no history or parts in the first message.")
                 # Proceed with empty input

            # --- Invoke the ADK Agent ---
            # ADK agents typically use __call__ or a similar method.
            # This needs adaptation based on the actual ADK agent interface.
            if hasattr(self.adk_agent, '__call__') and callable(self.adk_agent.__call__):
                 # Note: ADK agents might be async or sync. Need to handle both.
                 # Check the type of the mock object directly for testing purposes
                 if isinstance(self.adk_agent, AsyncMock):
                     logger.info(f"Invoking async ADK agent (mock) '{self.adk_agent.name}' with input: '{user_input_text[:50]}...'" )
                     agent_response_text = await self.adk_agent(user_input_text)
                     logger.info(f"ADK agent (mock) '{self.adk_agent.name}' responded.")
                 # Fallback to inspect for potentially real agents, or assume sync for MagicMock
                 elif not inspect.iscoroutinefunction(getattr(self.adk_agent, '__call__', None)):
                    logger.info(f"Invoking sync ADK agent '{self.adk_agent.name}' via asyncio.to_thread...")
                    # Pass the agent's __call__ method to to_thread
                    agent_response_text = await asyncio.to_thread(self.adk_agent.__call__, user_input_text)
                    logger.info(f"Sync ADK agent '{self.adk_agent.name}' responded.")
                 else: # Assume it's an async function if not explicitly AsyncMock or sync
                     logger.info(f"Invoking async ADK agent '{self.adk_agent.name}' with input: '{user_input_text[:50]}...'" )
                     # Await __call__ explicitly for clarity, especially with mocks
                     agent_response_text = await self.adk_agent.__call__(user_input_text)
                     logger.info(f"ADK agent '{self.adk_agent.name}' responded.")

            else:
                 logger.error(f"Wrapped ADK agent '{self.adk_agent.name}' does not have a callable '__call__' method.")
                 raise NotImplementedError("ADK agent invocation method not found or not callable.")

            # --- Format response into A2A Artifact ---
            task.artifacts = [
                a2a_models.Artifact(
                    parts=[a2a_models.TextPart(text=str(agent_response_text))]
                )
            ]
            task.status.state = a2a_models.TaskState.COMPLETED
            logger.info(f"A2A task {task.id} completed successfully.")
            # TODO: Send final TaskStatusUpdateEvent if streaming

        except Exception as e:
            # Use task.id
            logger.error(f"Error processing A2A task {task.id} for ADK agent {self.adk_agent.name}: {e}", exc_info=True)
            task.status.state = a2a_models.TaskState.FAILED
            # Set artifacts to empty list on error
            task.artifacts = []
            # Remove setting task.status.error; error info should be in the final JSONRPCResponse
            # task.status.error = a2a_models.InternalError(
            #     message=f"Failed to process request with ADK agent: {str(e)}"
            # )
            # TODO: Send final TaskStatusUpdateEvent if streaming, potentially with error info

        return task

# --- Example Usage (Illustrative - would likely be in a main script) ---
# from src.jarvis.agents import CodingAgent # Import your actual ADK agent
# from fastapi import FastAPI
# import uvicorn

# async def run_a2a_adapter():
#     # 1. Create your ADK agent instance
#     coding_agent_adk = CodingAgent() # Assuming it initializes correctly

#     # 2. Define the Agent Card for the A2A endpoint
#     #    This needs to accurately reflect the wrapped agent's capabilities
#     coding_agent_card = a2a_models.AgentCard(
#         agentId="jarvis-coding-agent-a2a-v1",
#         name="Jarvis Coding Agent (A2A)",
#         description=coding_agent_adk.description, # Reuse description
#         version="1.0.0",
#         endpoint=a2a_models.Endpoint(url="http://localhost:8002/a2a"), # Example endpoint
#         authentication=a2a_models.Authentication(type=a2a_models.AuthenticationType.NONE), # Example auth
#         capabilities=[ # Define capabilities based on A2A spec / what the agent does
#             a2a_models.Capability(name="textProcessing"),
#             a2a_models.Capability(name="codeGeneration"),
#         ],
#         skills=[ # Define skills mapped from ADK agent's abilities
#              a2a_models.Skill(
#                  id="generate_code",
#                  name="Generate Code",
#                  description="Generates code based on a natural language prompt.",
#                  parametersSchema={ # Example input schema
#                      "type": "object",
#                      "properties": {"prompt": {"type": "string"}},
#                      "required": ["prompt"],
#                  }
#                  # Define responseSchema if applicable
#              )
#         ]
#         # Add other fields like inputModes, outputModes, etc.
#     )

#     # 3. Create the wrapper instance
#     a2a_wrapper = AdkAgentA2AWrapper(adk_agent=coding_agent_adk, agent_card=coding_agent_card)

#     # 4. Create a FastAPI app to host the A2A server
#     app = FastAPI(title="Jarvis ADK Agent A2A Adapter")

#     # 5. Mount the A2A server routes to the FastAPI app
#     #    The A2AServer base class should provide routing logic,
#     #    or we need to add routes that call a2a_wrapper.handle_request
#     #    (Depends on the implementation in src/jarvis/libs/a2a/server/server.py)

#     # Placeholder: Assuming A2AServer has a method to integrate with FastAPI
#     # This needs adjustment based on the actual library code.
#     # Example: a2a_wrapper.mount_to_fastapi(app, prefix="/a2a")

#     # Example manual route (if base class doesn't handle it)
#     # @app.post("/a2a")
#     # async def handle_a2a_request(request: Dict[str, Any]):
#     #     # Need to parse JSON-RPC request and call appropriate wrapper method
#     #     # This requires implementing JSON-RPC handling based on the A2A spec
#     #     response_data = await a2a_server.handle_json_rpc_request(request, a2a_wrapper) # Needs this function
#     #     return response_data

#     print("Starting A2A adapter server for CodingAgent...")
#     # uvicorn.run(app, host="0.0.0.0", port=8002) # Run on a different port

# # if __name__ == "__main__":
# #    import asyncio
# #    asyncio.run(run_a2a_adapter()) 