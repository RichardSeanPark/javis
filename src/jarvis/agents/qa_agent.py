# src/jarvis/agents/qa_agent.py

from google.adk.agents import LlmAgent
import os

# Define the default model or get from environment variable if needed
DEFAULT_QA_MODEL = os.getenv("QA_AGENT_MODEL", "gemini-1.5-flash-latest") # Use same as dispatcher or a specific QA model
DEFAULT_QA_INSTRUCTION = (
    "You are a helpful Q&A assistant. Answer the user's question in English based on your internal knowledge. "
    "If the question requires current information or knowledge you don't possess, use the web_search tool. "
    "Synthesize the search results into a concise answer. Respond only in English."
)

class KnowledgeQA_Agent(LlmAgent):
    """
    Answers general knowledge questions in English.
    Can use web search for up-to-date information.
    """

    def __init__(self, **kwargs):
        """Initializes the KnowledgeQA_Agent."""
        name = kwargs.pop('name', "KnowledgeQA_Agent")
        description = kwargs.pop('description', "Answers general knowledge questions in English. Can use web search for up-to-date information.")
        model = kwargs.pop('model', DEFAULT_QA_MODEL)
        # Use the module-level default for instruction
        instruction_to_pass = kwargs.pop('instruction', DEFAULT_QA_INSTRUCTION)

        # TODO: Define and register tools (e.g., web search tool)
        # Example placeholder for tool registration
        # tools = kwargs.pop('tools', [])
        # search_tool = self._create_web_search_tool() # Method to create/get the tool
        # if search_tool:
        #     tools.append(search_tool)

        super().__init__(
            name=name,
            description=description,
            model=model,
            instruction=instruction_to_pass,
            # tools=tools, # Pass tools if defined
            **kwargs
        )
        # Set instruction on instance for potential direct access/testing
        self.instruction = instruction_to_pass
        # print(f"KnowledgeQA_Agent initialized with model: {self.model}, tools: {self.tools}")


    # --- Placeholder for Tool Interface ---
    # def _create_web_search_tool(self):
    #     # Placeholder: Logic to define or retrieve the web search tool
    #     # This will be implemented in Step 5 (Tool Definition)
    #     print("Placeholder: Web search tool would be created/registered here.")
    #     return None # Return the actual tool object later

    # The main logic will likely be handled by the LlmAgent's default invoke/run
    # based on the instruction and provided tools. Specific overrides can be added if needed. 