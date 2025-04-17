"""
입력 처리 결과를 위한 Pydantic 모델 정의
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ParsedInput(BaseModel):
    """
    입력 파서의 최종 출력 구조를 나타내는 데이터 모델
    """
    original_text: str = Field(..., description="사용자가 입력한 원본 텍스트")
    original_language: str = Field(..., description="감지된 원본 텍스트의 언어 코드 (ISO 639-1)")
    english_text: str = Field(..., description="원본 텍스트를 영어로 번역한 결과")
    intent: Optional[str] = Field(None, description="분석된 사용자의 주된 의도 (예: 'code_generation', 'question_answering')")
    entities: Optional[Dict[str, Any]] = Field(None, description="텍스트에서 추출된 주요 엔티티 정보")
    domain: Optional[str] = Field(None, description="식별된 요청의 주 도메인 (예: 'coding', 'general')") 