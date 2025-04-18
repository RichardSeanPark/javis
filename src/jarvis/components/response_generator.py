# src/jarvis/components/response_generator.py
import logging
from typing import Any, Optional

# Import the specific translation function for direct use
from ..tools.translate_tool import translate_text

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """
    Generates the final response for the user, including formatting
    and translation back to the original language if necessary.
    """

    def __init__(self):
        # In this version, we directly use the imported translate_text function.
        # Alternatively, the translate_tool object could be passed via dependency injection.
        logger.info("ResponseGenerator initialized.")
        # We might need an LLM client here later for advanced formatting/summarization.
        # self.llm_client = ...

    async def generate_response(self, english_result: Any, original_language: str) -> str:
        """
        Formats the result received from an agent and translates it back to the
        original user language if needed.

        Args:
            english_result: The result obtained from the agent/tool (expected to be primarily text for now).
            original_language: The ISO 639-1 code of the user's original input language (e.g., 'ko', 'en').

        Returns:
            The final response string, potentially translated.
        """
        logger.info(f"Generating final response for language: {original_language}")
        logger.debug(f"Received English result: {english_result}")

        default_empty_message = "I received an empty response."

        # Handle None input explicitly before formatting
        if english_result is None:
            logger.warning("Received None result from agent/tool.")
            return default_empty_message

        # 1. Format the result (Basic formatting for now)
        # TODO: Implement more sophisticated formatting, potentially using an LLM.
        # Handle potential non-string results gracefully.
        formatted_result: str
        if isinstance(english_result, str):
            formatted_result = english_result.strip()
        elif isinstance(english_result, dict) or isinstance(english_result, list):
             # Simple conversion for dict/list, improve later
             formatted_result = str(english_result)
        else:
             # Fallback for other types
             formatted_result = str(english_result) # This will turn None into 'None', handled above now.

        # Handle empty string result AFTER formatting
        if not formatted_result:
             logger.warning("Received empty string result from agent/tool after formatting.")
             formatted_result = default_empty_message

        # 2. Translate back to original language if necessary
        # Only translate if the language is not English AND the result is not the default empty message.
        if original_language != 'en' and formatted_result != default_empty_message:
            logger.info(f"Translating result from 'en' to '{original_language}'")
            try:
                # Use the imported translate_text function directly
                final_response = await translate_text(
                    text=formatted_result,
                    target_language=original_language,
                    source_language='en'
                )
                logger.info("Translation successful.")
                return final_response
            except Exception as e:
                logger.error(f"Error translating response to {original_language}: {e}", exc_info=True)
                # Fallback to returning the English result if translation fails
                logger.warning("Translation failed. Returning English result.")
                return formatted_result
        else:
            # If original language is English or result is empty, return as is
            logger.info("No translation needed or result is empty.")
            return formatted_result 