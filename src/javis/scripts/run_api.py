"""
자비스 API 서버 실행 스크립트
"""

import uvicorn
import argparse


def main():
    """
    API 서버 실행 메인 함수
    """
    parser = argparse.ArgumentParser(description="Jarvis API 서버 실행")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="서버 호스트 (기본값: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080, help="서버 포트 (기본값: 8080)")
    parser.add_argument("--reload", action="store_true", help="코드 변경 시 자동 재시작")
    
    args = parser.parse_args()
    
    print(f"Jarvis API 서버를 {args.host}:{args.port}에서 시작합니다...")
    uvicorn.run(
        "jarvis.interfaces.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main() 