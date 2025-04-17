"""
사용자 입력을 분석하여 ParsedInput 객체를 생성하는 에이전트
"""
import os
import json # json 모듈 임포트
from google.adk.agents import LlmAgent
# from google.adk.models import LlmConfig # 제거
from ..models.input import ParsedInput
# 필요시 추가 임포트 (예: Vertex AI 클라이언트)
# from google.generativeai.types import GenerationConfig # 필요 시
# from google.generativeai.types import Content, Part # 제거
import re # 정규 표현식 사용
import google.generativeai as genai
import asyncio # asyncio 임포트 추가

# API 키 설정 (환경 변수 사용)
try:
    # InputParserAgent 클래스 외부에서 한번만 설정 시도
    api_key = os.getenv("GEMINI_API_KEY") 
    if api_key:
        genai.configure(api_key=api_key)
        print("DEBUG: Genai API key configured.")
    else:
        print("Warning: GEMINI_API_KEY environment variable not found.")
except Exception as e:
    print(f"Error configuring Genai API key: {e}")

class InputParserAgent(LlmAgent):
    """
    사용자 입력을 받아 언어 감지, 번역, 의도/엔티티/도메인 분석을 수행하는 에이전트
    """
    def __init__(self):
        """
        InputParserAgent 초기화
        """
        # instruction은 ADK 에이전트 자체의 기본 동작 지침용으로 남겨둘 수 있음
        # (단, 현재 process_input에서는 사용하지 않음)
        instruction = (
            "This agent parses user input. It can detect language, translate, and analyze intent."
        )
        super().__init__(
            name="InputParser",
            description="Parses user input: detects language, translates to English, and analyzes intent, entities, and domain.",
            model="gemini-1.5-flash", # ADK 에이전트가 사용할 기본 모델 (현재 직접 사용 안함)
            instruction=instruction
        )
        # self.llm 디버깅 코드 제거

    async def process_input(self, user_input: str) -> ParsedInput:
        """
        사용자 입력을 처리하여 ParsedInput 객체를 반환합니다.
        """
        original_language = "en" # 기본값 영어
        english_text = user_input # 기본값은 원본 텍스트
        intent = None # 기본값
        entities = None # 기본값
        domain = None # 기본값

        # --- 언어 감지 (이전 단계에서 구현) ---
        try:
            lang_detection_prompt = (
                f"Detect the language of the following text and return only the ISO 639-1 code:\\n\\n"
                f"Text: {user_input}"
            )
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = await model.generate_content_async(lang_detection_prompt)

            final_response_text = response.text.strip().lower()
            match = re.search(r'\b([a-z]{2})\b', final_response_text)
            if match:
                original_language = match.group(1)
                print(f"DEBUG: Detected language: {original_language}")
            else:
                 print(f"Warning: Could not extract language code from response: {final_response_text}")
        except Exception as e:
            print(f"Error during language detection (using genai client): {e}")
            pass
        
        # API 호출 사이에 지연 추가
        await asyncio.sleep(1)

        # --- 2.4. 영어 번역 (original_language가 'en'이 아닌 경우) ---
        if original_language != "en":
            try:
                translation_prompt = (
                    f"Translate the following text from '{original_language}' to English:\\n\\n"
                    f"Text: {user_input}"
                )
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = await model.generate_content_async(translation_prompt)
                translated_text = response.text.strip()
                if translated_text:
                    english_text = translated_text # 번역 결과 저장
                    print(f"DEBUG: Translated to English: {english_text[:50]}...")
                else:
                    print("Warning: Translation result was empty.")
            except Exception as e:
                print(f"Error during translation (using genai client): {e}")
                pass
            
            # API 호출 사이에 지연 추가 (번역 수행 시)
            await asyncio.sleep(1)
        else:
             print("DEBUG: Input is already in English.")

        # --- 2.5. 의도/엔티티/도메인 분석 기능 구현 (english_text 사용) ---
        try:
            analysis_prompt = (
                f"Analyze the following English text. Identify the primary intent (e.g., code_generation, question_answering, document_summary), "
                f"extract key entities as a simple JSON object (key-value pairs), and determine the main domain (e.g., coding, finance, general). "
                f"Respond ONLY with a JSON object containing the keys 'intent', 'entities', and 'domain'. The value for 'entities' should be a JSON object itself or null. "
                f"Example format: "
                f"{{ \"intent\": \"example_intent\", \"entities\": {{ \"key1\": \"value1\" }}, \"domain\": \"example_domain\" }}\n\n"
                f"Text: {english_text}"
            )
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = await model.generate_content_async(analysis_prompt)
            
            # 응답에서 JSON 추출 시도
            response_text = response.text.strip()
            # LLM 응답에서 ```json ... ``` 블록 제거
            if response_text.startswith("```json"):
                response_text = response_text[7:].strip()
            if response_text.endswith("```"):
                response_text = response_text[:-3].strip()

            parsed_analysis = json.loads(response_text)

            intent = parsed_analysis.get("intent")
            entities = parsed_analysis.get("entities") # 이미 JSON 객체이거나 null
            domain = parsed_analysis.get("domain")
            print(f"DEBUG: Analysis result - Intent: {intent}, Entities: {entities}, Domain: {domain}")

        except json.JSONDecodeError as e:
            print(f"Error parsing analysis JSON response: {e}. Response text: {response_text}")
            # 오류 발생 시 기본값(None) 유지
        except Exception as e:
            print(f"Error during intent/entity/domain analysis: {e}")
            # 오류 발생 시 기본값(None) 유지
            pass

        # --- 2.6. ParsedInput 객체 생성 및 반환 ---
        return ParsedInput(
            original_text=user_input,
            original_language=original_language,
            english_text=english_text,
            intent=intent, # 분석 결과 또는 None
            entities=entities, # 분석 결과 또는 None
            domain=domain # 분석 결과 또는 None
        ) 