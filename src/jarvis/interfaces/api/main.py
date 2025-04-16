"""
Jarvis 커스텀 웹 UI를 위한 FastAPI 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="Jarvis API")

# CORS 설정 (프론트엔드와의 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 환경에서는 특정 출처만 허용해야 함
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """
    루트 엔드포인트
    """
    return {"message": "Welcome to Jarvis API"}

# 향후 추가될 기능:
# @app.post("/chat")
# async def chat_endpoint(request: ChatRequest):
#     """
#     채팅 엔드포인트: 사용자 메시지를 처리하고 응답을 반환
#     """
#     return {"response": "AI 응답"} 