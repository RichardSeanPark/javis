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
        try:
            # 별도의 genai 클라이언트로 언어 감지 수행
            lang_detection_prompt = (
                f"Detect the language of the following text and return only the ISO 639-1 code:\n\n"
                f"Text: {user_input}"
            )
            # 언어 감지용 모델 인스턴스 생성 (Agent의 model과 별개일 수 있음)
            model = genai.GenerativeModel('gemini-1.5-flash') 
            response = await model.generate_content_async(lang_detection_prompt) # 비동기 호출

            final_response_text = response.text.strip().lower()
            match = re.search(r'\b([a-z]{2})\b', final_response_text)
            if match:
                detected_lang_code = match.group(1)
                original_language = detected_lang_code
                print(f"DEBUG: Detected language: {original_language}")
            else:
                 print(f"Warning: Could not extract language code from response: {final_response_text}")
        
        except Exception as e:
            print(f"Error during language detection (using genai client): {e}")
            # 오류 발생 시 기본값(en) 사용
            pass

        # TODO: 2.4. 영어 번역 기능 구현 (마찬가지로 genai 클라이언트 사용)
        english_text = user_input
        if original_language != "en":
            pass

        # TODO: 2.5. 의도/엔티티/도메인 분석 기능 구현 (마찬가지로 genai 클라이언트 사용)
        intent = None
        entities = None
        domain = None

        return ParsedInput(
            original_text=user_input,
            original_language=original_language,
            english_text=english_text,
            intent=intent,
            entities=entities,
            domain=domain
        ) 