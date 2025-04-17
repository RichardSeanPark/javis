"""
사용자 입력을 분석하여 ParsedInput 객체를 생성하는 에이전트
"""

from google.adk.agents import LlmAgent
# from google.adk.models import LlmConfig # 제거
from ..models.input import ParsedInput
# 필요시 추가 임포트 (예: Vertex AI 클라이언트)

class InputParserAgent(LlmAgent):
    """
    사용자 입력을 받아 언어 감지, 번역, 의도/엔티티/도메인 분석을 수행하는 에이전트
    """
    def __init__(self):
        """
        InputParserAgent 초기화
        """
        super().__init__(
            name="InputParser",
            description="Parses user input: detects language, translates to English, and analyzes intent, entities, and domain.",
            model="gemini-1.5-flash"  # llm_config 대신 model 파라미터 사용
            # llm_config=LlmConfig(model_id="gemini-1.5-flash") # 제거
        )
        # 추가적인 초기화 (예: Vertex AI 클라이언트 초기화)는 여기에 구현

    async def process_input(self, user_input: str) -> ParsedInput:
        """
        사용자 입력을 처리하여 ParsedInput 객체를 반환합니다.

        Args:
            user_input: 사용자가 입력한 원본 텍스트

        Returns:
            처리된 결과를 담은 ParsedInput 객체
        """
        # TODO: 언어 감지, 번역, 의도/엔티티/도메인 분석 로직 구현
        
        # 임시 반환값 (구현 전)
        return ParsedInput(
            original_text=user_input,
            original_language="ko",  # 임시
            english_text=user_input, # 임시
            intent=None,
            entities=None,
            domain=None
        ) 