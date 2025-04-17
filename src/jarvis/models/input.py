"""
입력 파싱 결과를 담는 데이터 모델 정의
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ParsedInput(BaseModel):
    """
    사용자 입력 파싱 결과를 위한 데이터 모델
    
    입력 텍스트의 언어 감지, 영어 번역, 의도 분석 및 엔티티 추출 결과를 포함합니다.
    """
    
    original_text: str = Field(
        description="사용자가 입력한 원본 텍스트"
    )
    
    original_language: str = Field(
        description="감지된 원본 텍스트의 언어 코드 (ISO 639-1, 예: 'ko', 'en')"
    )
    
    english_text: str = Field(
        description="원본 텍스트를 영어로 번역한 결과 (원본이 영어인 경우 동일)"
    )
    
    intent: Optional[str] = Field(
        default=None,
        description="분석된 사용자의 주된 의도 (예: 'code_generation', 'question_answering')"
    )
    
    entities: Optional[Dict[str, Any]] = Field(
        default=None,
        description="텍스트에서 추출된 주요 엔티티 정보"
    )
    
    domain: Optional[str] = Field(
        default=None,
        description="식별된 요청의 주 도메인 (예: 'coding', 'general')"
    ) 