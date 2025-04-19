# src/jarvis/agents/coding_agent.py

from google.adk.agents import LlmAgent
# Remove Field import if instruction is no longer a Field
# from pydantic import Field
import os # For potential env var usage

# Import the specific tool
from ..tools import code_execution_tool

# Define the default model or get from environment variable if needed
DEFAULT_CODING_MODEL = os.getenv("CODING_AGENT_MODEL", "gemini-1.5-flash-latest") # Example: Use same as dispatcher or a specific code model
DEFAULT_AGENT_INSTRUCTION = ( # Define as a module-level constant
    "You are an expert coding assistant. Analyze the provided English request "
    "and any accompanying code snippets. Generate improved code, explain code, "
    "debug errors, or optimize code as requested. Use the available tools "
    "for code execution or linting if necessary and permitted. "
    "Respond only in English with the code result or explanation."
)

class CodingAgent(LlmAgent):
    """
    Generates, analyzes, debugs, and optimizes code based on user requests in English.
    Can use tools like a code executor.
    """
    # Remove the Field definition for instruction here
    # instruction: str = Field(...)

    def __init__(self, **kwargs):
        """Initializes the CodingAgent and registers required tools."""
        # Ensure name and description are set, defaulting if not provided
        name = kwargs.pop('name', "CodingAgent")
        description = kwargs.pop('description', "Generates, analyzes, debugs, and optimizes code based on user requests in English.")
        # Set the model, using default if not provided in kwargs
        model = kwargs.pop('model', DEFAULT_CODING_MODEL)
        # Get instruction from kwargs or use the module-level default constant
        instruction_to_pass = kwargs.pop('instruction', DEFAULT_AGENT_INSTRUCTION)

        # Explicitly define the tools required by this agent
        # Get any tools passed via kwargs and add our specific tool
        tools = kwargs.pop('tools', [])
        if code_execution_tool not in tools:
             tools.append(code_execution_tool)

        # Initialize the parent LlmAgent class
        # Pass name, description, model, instruction, and the tools list
        super().__init__(
            name=name,
            description=description,
            model=model,
            instruction=instruction_to_pass, # Pass the resolved instruction
            tools=tools, # Pass the list including the code execution tool
            **kwargs
        )
        # Set the instruction attribute on the instance *after* super().__init__
        # This might be redundant if LlmAgent already sets it, but ensures it exists
        self.instruction = instruction_to_pass
        # Add log after super().__init__
        # print(f"CodingAgent initialized with model: {self.model}, tools: {[t.name for t in self.tools]}")


    # --- Tool Interface Definition (Implicit via Registration) ---
    # By registering 'code_execution_tool', the agent expects a tool with
    # the name 'execute_python_code' and its defined signature (code: str) -> str.
    # The actual tool object is imported and passed during initialization.

    # The main logic will likely be handled by the LlmAgent's default invoke/run
    # based on the instruction and provided tools. Specific overrides can be added if needed. 