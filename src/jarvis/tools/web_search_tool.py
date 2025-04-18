# src/jarvis/tools/web_search_tool.py
import asyncio
import logging
# from google.adk.tools import Tool # Previous attempt
from google.adk.tools import FunctionTool # Correct import based on installed package structure
from duckduckgo_search import DDGS # Correct import

# TODO: Implement actual web search logic (e.g., using Google Search API, Tavily, etc.)
# This is a placeholder using duckduckgo_search

logger = logging.getLogger(__name__)

async def web_search(query: str) -> str:
    """
    Searches the web for the given query using DuckDuckGo and returns the top results.

    Args:
        query: The search query string.

    Returns:
        A string containing the formatted search results, or an error message.
    """
    logger.info(f"Performing web search for query: {query}")
    try:
        async with DDGS() as ddgs:
            results = await ddgs.atext(query, max_results=5) # Use async method atext

        if not results:
            logger.info("No search results found.")
            return "No relevant information found on the web for your query."

        formatted_results = "Web Search Results:\n"
        for i, result in enumerate(results, 1):
            formatted_results += f"{i}. {result.get('title', 'No Title')}\n"
            formatted_results += f"   URL: {result.get('href', 'No URL')}\n"
            formatted_results += f"   Snippet: {result.get('body', 'No Snippet')}\n\n"

        # TODO: Optionally, summarize the results using an LLM
        # summary_prompt = f"Summarize the following search results relevant to the query '{query}':\n\n{formatted_results}"
        # summary = await call_llm_for_summary(summary_prompt) # Replace with actual LLM call
        # return summary

        logger.info(f"Web search successful. Returning {len(results)} results.")
        return formatted_results.strip()

    except Exception as e:
        logger.error(f"Error during web search for '{query}': {e}", exc_info=True)
        return f"An error occurred while searching the web: {e}"

# Create the ADK Tool object
# web_search_tool = FunctionTool.from_function( # Incorrect usage
#     func=web_search,
#     description="Searches the web for the given query and returns relevant information snippets and URLs.", # Description is taken from docstring
# )
web_search_tool = FunctionTool(func=web_search) # Correct usage: pass the function to the constructor

# Example usage (for testing purposes)
async def main():
    search_results = await web_search("latest AI advancements")
    print(search_results)

if __name__ == "__main__":
    # Note: Running this directly might cause issues if the event loop is already running elsewhere (e.g., in ADK).
    # It's better to test tools through an agent or dedicated test scripts.
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot run new event loop" in str(e):
            print("Cannot run example directly when an event loop is already running.")
        else:
            raise e 