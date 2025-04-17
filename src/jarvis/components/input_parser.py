"""
사용자 입력을 분석하여 ParsedInput 객체를 생성하는 에이전트
"""
import os
from google.adk.agents import LlmAgent
# from google.adk.models import LlmConfig # 제거
from ..models.input import ParsedInput
# 필요시 추가 임포트 (예: Vertex AI 클라이언트)
# from google.generativeai.types import GenerationConfig # 필요 시
# from google.generativeai.types import Content, Part # 제거
import re # 정규 표현식 사용
import google.generativeai as genai

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
        
        # --- 언어 감지 (이전 단계에서 구현) ---
        try:
            lang_detection_prompt = (
                f"Detect the language of the following text and return only the ISO 639-1 code:\n\n"
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

        # --- 2.4. 영어 번역 (original_language가 'en'이 아닌 경우) ---
        if original_language != "en":
            try:
                translation_prompt = (
                    f"Translate the following text from '{original_language}' to English:\n\n"
                    f"Text: {user_input}"
                )
                # 번역용 모델 인스턴스 (동일 모델 사용 가능)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = await model.generate_content_async(translation_prompt)
                translated_text = response.text.strip()
                if translated_text:
                    english_text = translated_text # 번역 결과 저장
                    print(f"DEBUG: Translated to English: {english_text[:50]}...")
                else:
                    print("Warning: Translation result was empty.")
                    # 번역 실패 시 원본 텍스트 유지 (기본값)
            except Exception as e:
                print(f"Error during translation (using genai client): {e}")
                # 오류 발생 시 원본 텍스트 유지 (기본값)
                pass
        else:
             # 이미 영어인 경우 디버그 메시지 출력
             print("DEBUG: Input is already in English.")

        # TODO: 2.5. 의도/엔티티/도메인 분석 기능 구현 (english_text 사용)
        intent = None
        entities = None
        domain = None

        return ParsedInput(
            original_text=user_input,
            original_language=original_language,
            english_text=english_text, # 번역 결과 또는 원본
            intent=intent,
            entities=entities,
            domain=domain
        ) 