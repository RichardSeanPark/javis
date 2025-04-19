# src/jarvis/components/response_generator.py
import logging
from typing import Any, Optional

# Import the specific translation function for direct use
from ..tools.translate_tool import translate_text

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Processes results from agents and generates the final user-facing response,
    handling translation back to the original language.
    """

    def __init__(self):
        """Initializes the ResponseGenerator."""
        # If translate_tool is needed, it could be initialized here or passed
        # self.translator = translate_tool # Example
        logger.info("ResponseGenerator initialized.")
        # We might need an LLM client here later for advanced formatting/summarization.
        # self.llm_client = ...

    async def generate_response(self, english_result: Any, original_language: Optional[str]) -> str:
        """
        Generates the final response string for the user.

        Args:
            english_result: The result received from the agent (assumed to be in English).
            original_language: The original language code of the user's request (e.g., 'ko', 'en').

        Returns:
            The final response string, translated to the original language if necessary.
        """
        logger.info(f"Generating response for result (type: {type(english_result)}), original language: {original_language}")

        # 1. Format the English result into a string (basic implementation)
        if isinstance(english_result, str):
            formatted_english_response = english_result
        elif english_result is None:
            formatted_english_response = "I received an empty response from the agent."
        else:
            # Basic conversion for non-string results
            try:
                formatted_english_response = str(english_result)
                logger.debug(f"Converted non-string result to string: {formatted_english_response[:100]}...")
            except Exception as e:
                logger.error(f"Error converting agent result to string: {e}", exc_info=True)
                formatted_english_response = "I encountered an issue processing the result."

        # 2. Translate if necessary (Placeholder - actual translation logic later)
        if original_language and original_language != 'en':
            logger.info(f"Translation needed to {original_language}. (Translation logic placeholder)")
            # TODO: Implement translation using translate_tool
            # Example (requires translator setup):
            # final_response = await self.translator.translate_text(formatted_english_response, target_language=original_language)
            # For now, return English with a note
            final_response = f"(In English, as translation is not yet implemented): {formatted_english_response}"
        else:
            logger.info("No translation needed or original language is English.")
            final_response = formatted_english_response

        logger.info(f"Final generated response: {final_response[:100]}...")
        return final_response 