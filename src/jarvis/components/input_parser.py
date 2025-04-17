"""
사용자 입력을 분석하고 파싱하는 에이전트 모듈

이 모듈은 입력 텍스트의 언어를 감지하고, 필요시 영어로 번역하며,
사용자의 의도와 주요 엔티티를 분석하여 ParsedInput 객체를 생성합니다.
"""

import asyncio
import json
from typing import Optional, Dict, Any

from google.adk import Agent
import google.generativeai as genai
from dotenv import load_dotenv
import os

from src.jarvis.models.input import ParsedInput

# 환경 변수 로드
load_dotenv()

# Gemini API 키 설정
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)


class InputParserAgent(Agent):
    """
    사용자 입력을 분석하여 언어 감지, 번역, 의도 분석 등을 수행하는 에이전트
    
    이 에이전트는 다음 기능을 수행합니다:
    1. 텍스트 언어 감지
    2. 영어가 아닌 경우 영어로 번역
    3. 사용자 의도 및 엔티티 분석
    4. 분석 결과를 ParsedInput 객체로 반환
    """
    
    def __init__(self):
        """
        InputParserAgent 초기화
        """
        super().__init__(
            name="InputParser",
            description="Analyzes and parses user input, detecting language and extracting intent and entities."
        )
        # Gemini 모델 설정
        self.model = genai.GenerativeModel("gemini-pro")
    
    async def process_input(self, user_input: str) -> ParsedInput:
        """
        사용자 입력을 처리하여 ParsedInput 객체 반환
        
        Args:
            user_input: 처리할 사용자 입력 텍스트
            
        Returns:
            처리된 입력 정보를 담은 ParsedInput 객체
        """
        # 1. 언어 감지
        original_language = await self._detect_language(user_input)
        
        # 2. 영어로 번역 (필요한 경우)
        english_text = user_input
        if original_language != "en":
            english_text = await self._translate_to_english(user_input, original_language)
        
        # 3. 의도 및 엔티티 분석
        intent, entities, domain = await self._analyze_intent_and_entities(english_text)
        
        # 4. ParsedInput 객체 생성 및 반환
        return ParsedInput(
            original_text=user_input,
            original_language=original_language,
            english_text=english_text,
            intent=intent,
            entities=entities,
            domain=domain
        )
    
    async def _detect_language(self, text: str) -> str:
        """
        텍스트의 언어를 감지하여 ISO 639-1 코드 반환
        
        Args:
            text: 언어를 감지할 텍스트
            
        Returns:
            감지된 언어의 ISO 639-1 코드 (예: 'ko', 'en', 'ja')
        """
        prompt = f"Detect the language of the following text and return only the ISO 639-1 code:\n\nText: {text}"
        
        response = await asyncio.to_thread(
            self.model.generate_content, 
            prompt
        )
        
        # 응답에서 언어 코드 추출 (줄바꿈, 공백 제거)
        lang_code = response.text.strip().lower()
        
        # 일반적인 ISO 639-1 코드는 2자리
        if len(lang_code) > 2:
            # 응답이 더 길다면 처음 2자만 사용
            lang_code = lang_code[:2]
        
        return lang_code
    
    async def _translate_to_english(self, text: str, source_language: str) -> str:
        """
        텍스트를 영어로 번역
        
        Args:
            text: 번역할 텍스트
            source_language: 원본 텍스트의 언어 코드 (ISO 639-1)
            
        Returns:
            영어로 번역된 텍스트
        """
        prompt = f"Translate the following text from {source_language} to English:\n\nText: {text}"
        
        response = await asyncio.to_thread(
            self.model.generate_content, 
            prompt
        )
        
        return response.text.strip()
    
    async def _analyze_intent_and_entities(self, english_text: str) -> tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        영어 텍스트에서 의도, 엔티티, 도메인 분석
        
        Args:
            english_text: 분석할 영어 텍스트
            
        Returns:
            (intent, entities, domain) 튜플
        """
        prompt = f"""
        Analyze the following English text. Extract and provide the following information in JSON format:
        
        1. primary_intent: The main intent of the user (e.g., 'code_generation', 'question_answering', 'information_request')
        2. entities: Key entities mentioned in the text as a JSON object
        3. domain: The main domain or category of the request (e.g., 'coding', 'general_knowledge', 'math')
        
        Text: {english_text}
        
        Respond with ONLY a JSON object containing these three fields.
        """
        
        response = await asyncio.to_thread(
            self.model.generate_content, 
            prompt
        )
        
        # JSON 분석
        try:
            # 응답 텍스트에서 JSON 부분 추출 (코드 블록이나 여분의 텍스트 제거)
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(text)
            
            intent = result.get("primary_intent")
            entities = result.get("entities")
            domain = result.get("domain")
            
            return intent, entities, domain
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # JSON 파싱 실패 시 None 반환
            print(f"Error analyzing intent and entities: {e}")
            return None, None, None 