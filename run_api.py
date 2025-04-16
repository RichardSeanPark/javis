#!/usr/bin/env python
"""
자비스 API 서버 실행을 위한 편의 스크립트
"""

import uvicorn

if __name__ == "__main__":
    print("자비스 API 서버를 시작합니다...")
    uvicorn.run(
        "src.jarvis.interfaces.api.main:app",
        host="0.0.0.0",
        port=8088,
        reload=True,
    ) 