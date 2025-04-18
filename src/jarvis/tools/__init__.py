"""Module for registering available tools."""

from .translate_tool import translate_tool
# Import other tools here as they are created
# from .web_search_tool import web_search_tool
# from .code_execution_tool import code_execution_tool

# List of available tools for the dispatcher or agents to use
available_tools = [
    translate_tool,
    # web_search_tool,
    # code_execution_tool,
]
