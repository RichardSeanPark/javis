# src/jarvis/tools/web_search_tool.py
import asyncio
import logging
import os # For API Key and Model Name
import google.generativeai as genai # Import genai for summarization
# from google.adk.tools import Tool # Previous attempt
from google.adk.tools import FunctionTool # Correct import based on installed package structure
from duckduckgo_search import DDGS # Correct import
import dotenv # For loading .env

# Load .env file for API key and model name (if not already loaded globally)
# Consider if this should be handled at a higher level (e.g., Dispatcher init)
dotenv.load_dotenv()

# TODO: Implement actual web search logic (e.g., using Google Search API, Tavily, etc.)
# This is a placeholder using duckduckgo_search

logger = logging.getLogger(__name__)

# Configure genai (only if API_KEY is available)
API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_MODEL_NAME = os.getenv("VERTEX_MODEL_NAME", "gemini-1.5-flash-latest")
LLM_CLIENT_INITIALIZED = False
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        LLM_CLIENT_INITIALIZED = True
        logger.info("Genai configured successfully for web search summarization.")
    except Exception as e:
        logger.error(f"Error configuring genai for summarization: {e}")
else:
    logger.warning("GEMINI_API_KEY not found. Web search summarization will be disabled.")

async def web_search(query: str) -> str:
    """
    Searches the web for the given query using DuckDuckGo, summarizes the results using an LLM,
    and returns the summary or raw results if summarization fails.

    Args:
        query: The search query string.

    Returns:
        A string containing the summarized search results, raw results with an error message,
        or an error message if the search itself fails.
    """
    logger.info(f"Performing web search for query: {query}")
    try:
        async with DDGS() as ddgs:
            # Fetch slightly more results to provide better context for summarization
            results = await ddgs.atext(query, max_results=7)

        if not results:
            logger.info("No search results found.")
            return "No relevant information found on the web for your query."

        formatted_results = ""
        raw_content_for_summary = []
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No Title')
            url = result.get('href', 'No URL')
            body = result.get('body', 'No Snippet')
            formatted_results += f"{i}. {title}\n   URL: {url}\n   Snippet: {body}\n\n"
            # Collect content for the summary prompt
            raw_content_for_summary.append(f"Title: {title}\nSnippet: {body}")

        # --- LLM Summarization ---
        summary = None
        if LLM_CLIENT_INITIALIZED and raw_content_for_summary:
            # Only summarize if there's enough content and LLM is ready
            full_raw_text = "\n\n".join(raw_content_for_summary)
            # Heuristic: Summarize only if the combined text is reasonably long
            if len(full_raw_text) > 200: # Avoid summarizing very short results
                try:
                    logger.info(f"Attempting to summarize web search results for query: '{query}'")
                    model = genai.GenerativeModel(DEFAULT_MODEL_NAME)
                    summary_prompt = (
                        f"Based on the following web search results for the query '{query}', "
                        f"provide a concise summary in English answering the query. "
                        f"Focus on the most relevant information and synthesize the findings. "
                        f"Do not just list the results. Aim for 2-4 sentences.\n\n"
                        f"Search Results Snippets:\n{full_raw_text}"
                    )
                    # Use generate_content_async for async operation
                    response = await model.generate_content_async(summary_prompt)
                    summary = response.text
                    logger.info("Successfully summarized web search results.")
                except Exception as e:
                    logger.error(f"Error during LLM summarization for query '{query}': {e}", exc_info=True)
                    # Proceed without summary if LLM fails
            else:
                logger.info("Search results too short, skipping summarization.")
        elif not LLM_CLIENT_INITIALIZED:
             logger.warning("LLM client not initialized, skipping summarization.")
        # --- End LLM Summarization ---

        if summary:
            # Return summary prepended with a note, and maybe top 1-3 raw results for reference?
            # For now, just return the summary clearly marked.
            final_response = f"Summary based on web search results for '{query}':\n{summary}"
            # Optionally add top N raw results here if desired
            # final_response += "\n\nTop Raw Results:\n" + "\n".join(formatted_results.split('\n\n')[:3]) # Example: Add top 3
            logger.info(f"Web search and summarization successful for query: '{query}'")
            return final_response
        else:
            # Return raw results if summarization wasn't attempted or failed
            logger.info(f"Web search successful (no summary). Returning raw results for query: '{query}'")
            # Add a note if summarization failed due to an error
            error_note = ""
            if LLM_CLIENT_INITIALIZED and len(raw_content_for_summary) > 0 and len(full_raw_text) > 200 and summary is None : # Check if summary attempt was expected but failed
                 error_note = "\n(Note: Summarization failed, showing raw results)"
            return f"Web Search Results for '{query}':{error_note}\n\n{formatted_results.strip()}"

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
    # Test with summarization
    print("--- Testing with query likely needing summarization ---")
    search_results_long = await web_search("benefits of async programming in python")
    print(search_results_long)
    print("\n" + "="*20 + "\n")

    # Test with query likely not needing summarization (or short results)
    print("--- Testing with potentially short results ---")
    search_results_short = await web_search("python duckduckgo_search library pypi")
    print(search_results_short)
    print("\n" + "="*20 + "\n")

    # Test search failure (difficult to trigger reliably without network manipulation)
    # print("--- Testing search failure (simulated) ---")
    # Add mocking here if needed for robust testing

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