"""Translation tool using Generative AI."""

import google.genai as genai # Use the updated alias
from google.ai import generativelanguage as glm # Import for protos replacement
from google.ai.generativelanguage import Type as glm_Type # Import Type enum
from google.cloud import aiplatform # Import necessary for potential future use or consistency
from google.genai.types import Tool, FunctionDeclaration, Content, Part # Import FunctionDeclaration, Content, Part
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Configure the generative AI client
try:
    # Assuming genai.configure is still the correct method for the new library
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    # Consider adding Vertex AI initialization if needed later
    # aiplatform.init(project=os.getenv("GCP_PROJECT_ID"), location="us-central1")
except AttributeError:
     logging.warning("genai.configure not found. Assuming client is configured elsewhere or implicitly.")
except Exception as e:
    logging.error(f"Error configuring generative AI: {e}")
    # Handle configuration error appropriately

# Initialize the genai Client at module level
API_KEY = os.getenv("GEMINI_API_KEY")
client = None
if API_KEY:
    try:
        client = genai.Client(api_key=API_KEY)
        logging.info("Successfully initialized genai.Client with API key.")
    except Exception as e:
        logging.error(f"Failed to initialize genai.Client with API key: {e}")
else:
    logging.warning("GEMINI_API_KEY not found. genai.Client initialization skipped.")

# Define the translation function (removed default value for source_language)
async def translate_text(text: str, target_language: str, source_language: str) -> str:
    """Translates text to the target language using an LLM.

    Args:
        text: The text to translate.
        target_language: The target language code (ISO 639-1, e.g., 'ko', 'en').
        source_language: The source language code (ISO 639-1, e.g., 'ko', 'en').
                         An empty string or 'auto' can imply auto-detection but must be handled explicitly now.

    Returns:
        The translated text, or the original text if translation fails.
    """
    # Use the module-level client if available
    if not client:
        logging.error("genai.Client is not initialized. Cannot perform translation.")
        return text # Return original text if client is not available

    try:
        # Choose a model suitable for translation tasks
        model_name = 'gemini-1.5-flash-latest' # Define the model name to use

        # Handle source_language explicitly if auto-detection is desired
        prompt_source_lang = source_language
        if not source_language or source_language.lower() == 'auto':
            prompt = f"Translate the following text to {target_language}:\n\n{text}"
            prompt_source_lang = "auto-detected"
        else:
            prompt = f"Translate the following text from {source_language} to {target_language}:\n\n{text}"

        logging.info(f"Sending translation request to LLM (source: {prompt_source_lang}). Prompt: {prompt[:100]}..." )
        # Call generate_content using the client instance
        response = await client.aio.models.generate_content(
            model=model_name, # Specify the model
            contents=[Content(parts=[Part(text=prompt)])]
        )

        # Accessing response text might differ in google.genai
        # Check the actual response object structure if errors occur
        translated_text = "" # Initialize
        if response and hasattr(response, 'text') and response.text:
            translated_text = response.text.strip()
        elif response and hasattr(response, 'parts'): # Handle potential streaming response or different structure
             translated_text = "".join(part.text for part in response.parts).strip()

        if translated_text:
             logging.info(f"Translation successful. Result: {translated_text[:100]}...")
             return translated_text
        else:
            logging.warning(f"LLM response for translation was empty or invalid. Response: {response}")
            return text # Return original text on failure

    except Exception as e:
        logging.error(f"Error during translation LLM call: {e}")
        return text # Return original text on error

# Create the ADK Tool object using FunctionDeclaration.from_callable_with_api_option
# Create the FunctionDeclaration first, specifying the API option
func_decl = FunctionDeclaration.from_callable_with_api_option(callable=translate_text, api_option='GEMINI_API')
# Then create the Tool object using the declaration
translate_tool = Tool(function_declarations=[func_decl])

# Example usage (for testing purposes)
async def main():
    test_text_ko = "안녕하세요, 반갑습니다."
    test_text_en = "Hello, nice to meet you."

    translated_en = await translate_text(test_text_ko, 'en', 'ko')
    print(f"'{test_text_ko}' (ko) to English: {translated_en}")

    translated_ko = await translate_text(test_text_en, 'ko', 'en')
    print(f"'{test_text_en}' (en) to Korean: {translated_ko}")

    translated_fr = await translate_text(test_text_en, 'fr', 'en') # Auto source
    print(f"'{test_text_en}' (auto) to French: {translated_fr}")

if __name__ == "__main__":
    import asyncio
    # Check if running in a context with an event loop (like Jupyter)
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(main())
    except RuntimeError:
        # If no running loop, start a new one
        asyncio.run(main()) 