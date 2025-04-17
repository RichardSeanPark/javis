"""
사용자 입력을 분석하여 ParsedInput 객체를 생성하는 에이전트
"""
import os
import json # json 모듈 임포트
from google.adk.agents import BaseAgent
# from google.adk.models import LlmConfig # 제거
from ..models.input import ParsedInput
# 필요시 추가 임포트 (예: Vertex AI 클라이언트)
# from google.generativeai.types import GenerationConfig # 필요 시
from google.genai.types import Content, Part, GenerateContentResponse
import re # 정규 표현식 사용
import google.genai as genai
import asyncio # asyncio 임포트 추가
import logging
from typing import Optional, Dict, Any
from google.api_core import retry_async
from google.api_core import exceptions as api_exceptions
from dotenv import load_dotenv
from pydantic import Field
from google.api_core.retry import Retry, if_transient_error # if_transient_error 추가
from google.api_core.retry_async import AsyncRetry # AsyncRetry 임포트

# API 키 설정 (환경 변수 사용)
# 모듈 수준 configure는 dispatcher.py에서 처리하므로 여기서는 제거 또는 주석 처리
# try:
#     # InputParserAgent 클래스 외부에서 한번만 설정 시도
#     api_key = os.getenv("GEMINI_API_KEY") 
#     if api_key:
#         genai.configure(api_key=api_key)
#         print("DEBUG: Genai API key configured.")
#     else:
#         print("Warning: GEMINI_API_KEY environment variable not found.")
# except Exception as e:
#     print(f"Error configuring Genai API key: {e}")

class InputParserAgent(BaseAgent):
    """
    사용자 입력을 받아 언어 감지, 번역, 의도/엔티티/도메인 분석을 수행하는 에이전트
    (BaseAgent를 상속하여 자체 LLM 호출 로직 사용)
    """
    # 필요한 경우 자체 필드 정의 (예: 사용할 모델 이름 등)
    model_name: str = Field(default="gemini-pro") # 사용할 모델 이름 필드 추가
    # Pydantic 필드로 llm 선언 추가 (Client 객체로 변경)
    llm: Optional[genai.Client] = None # genai.Client 타입으로 변경
    # instruction: str = Field(default="...") # 필요시 자체 instruction 필드 추가

    def __init__(self, **kwargs):
        """InputParserAgent 초기화"""
        # BaseAgent의 __init__ 호출 시 model, instruction 전달 제거
        super().__init__(name="InputParserAgent", description="Parses user input for language, intent, entities, and domain.")
        # kwargs 처리 (Pydantic이 자동으로 처리할 수도 있음)
        # for key, value in kwargs.items():
        #     if hasattr(self, key):
        #         setattr(self, key, value)

        # LLM 클라이언트 초기화 (BaseAgent는 llm 객체를 자동으로 만들지 않음)
        self.llm = None
        # API 키 로드 (모듈 수준 configure에 의존하지 않고 직접 로드 및 사용)
        load_dotenv() 
        api_key_input = os.getenv("GEMINI_API_KEY")
        if not api_key_input:
            print("Warning: GEMINI_API_KEY not found for InputParserAgent.")
        else:
            try:
                # Client 생성 시 API 키 명시적 전달
                self.llm = genai.Client(api_key=api_key_input)
                print(f"InputParserAgent initialized with genai.Client using provided API key.")
            except Exception as e:
                print(f"Error initializing Genai client for InputParserAgent with API key: {e}")

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
            # model = genai.GenerativeModel('gemini-2.0-flash-exp') # 이전
            # response = await model.generate_content_async(lang_detection_prompt) # 이전
            response_text = await self._call_llm(lang_detection_prompt, model_id='gemini-2.0-flash-exp') # _call_llm 사용
            final_response_text = response_text.strip().lower()
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
        await asyncio.sleep(2)

        # --- 2.4. 영어 번역 (original_language가 'en'이 아닌 경우) ---
        if original_language != "en":
            try:
                translation_prompt = (
                    f"Translate the following text from '{original_language}' to English:\\n\\n"
                    f"Text: {user_input}"
                )
                # model = genai.GenerativeModel('gemini-2.0-flash-exp') # 이전
                # response = await model.generate_content_async(translation_prompt) # 이전
                translated_text = await self._call_llm(translation_prompt, model_id='gemini-2.0-flash-exp') # _call_llm 사용
                if translated_text:
                    english_text = translated_text # 번역 결과 저장
                    print(f"DEBUG: Translated to English: {english_text[:50]}...")
                else:
                    print("Warning: Translation result was empty.")
            except Exception as e:
                print(f"Error during translation (using genai client): {e}")
                pass
            
            # API 호출 사이에 지연 추가 (번역 수행 시)
            await asyncio.sleep(2)
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
            # model = genai.GenerativeModel('gemini-2.0-flash-exp') # 이전
            # response = await model.generate_content_async(analysis_prompt) # 이전
            response_text = await self._call_llm(analysis_prompt, model_id='gemini-2.0-flash-exp') # _call_llm 사용
            
            # 응답에서 JSON 추출 시도
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

    # _call_llm 메서드에서 self.llm 사용 확인
    @AsyncRetry(retry=if_transient_error, initial=1.0, maximum=10.0, multiplier=2.0) # AsyncRetry 사용
    async def _call_llm(self, prompt: str, model_id: str = "gemini-pro") -> str:
        """LLM 호출 (재시도 포함) - client.aio.models.generate_content 사용"""
        if not self.llm:
            logging.error("LLM client not initialized in InputParserAgent.")
            return "Error: LLM not available."
        try:
            # 새로운 SDK 방식 (dispatcher.py 와 동일하게)
            logging.debug(f"Calling InputParser LLM ({model_id}) with prompt: {prompt[:100]}...")
            # 수정: aio.models 사용
            response = await self.llm.aio.models.generate_content(
                model=model_id, # 사용할 모델 ID
                # prompt를 Content 객체 리스트로 변환
                contents=[Content(parts=[Part(text=prompt)])]
            )
            # response 처리 수정: response.text 직접 사용
            if hasattr(response, 'text'):
                return response.text
            else:
                # 에러 로깅 추가: .text 속성이 없는 경우
                logging.warning(f"LLM response object does not have a 'text' attribute. Type: {type(response)}, Content: {response}")
                return "Error: Could not extract text from LLM response."

        except AttributeError as ae:
            # 수정된 호출 방식에 대한 오류 처리 업데이트
            logging.error(f"AttributeError during InputParser LLM call (using aio.models.generate_content): {ae}", exc_info=True)
            return f"Error during LLM call (AttributeError): {ae}"
        except Exception as e:
            logging.error(f"Error calling LLM ({model_id}): {e}", exc_info=True)
            return f"Error during LLM call: {e}"

    async def _run_async_impl(self, *args, **kwargs):
        # BaseAgent를 상속하므로 _run_async_impl 또는 유사한 메서드 구현 필요
        # 에이전트가 직접 실행될 때의 로직 (예: process_input 호출)
        # ADK Runner가 호출하는 기본 메서드
        # 여기서는 간단히 NotImplementedError를 발생시키거나 기본 동작 정의
        # raise NotImplementedError("_run_async_impl not implemented for InputParserAgent")
        print("InputParserAgent._run_async_impl called (default behavior)")
        # 또는 입력 컨텍스트를 받아 process_input을 호출하도록 구현
        # ctx = InvocationContext(...) # 컨텍스트 얻는 방법 확인 필요
        # input_text = ... # 컨텍스트에서 입력 텍스트 추출
        # result = await self.process_input(input_text)
        # ctx.set_agent_response(result) # 결과 설정

        pass # Placeholder, 실제 로직 복원 필요 