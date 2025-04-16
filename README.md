# Jarvis AI Framework

자비스 AI 프레임워크 - 다국어 지원이 가능한 모듈식 AI 어시스턴트 프레임워크

## 소개

Jarvis AI Framework는 다양한 도메인과 언어를 지원하는 확장 가능한 AI 어시스턴트 프레임워크입니다. Google Agent Development Kit(ADK)와 Vertex AI를 기반으로 구축되었으며, 다양한 특수 에이전트, 도구 및 확장 모듈을 지원합니다.

## 주요 기능

- **다국어 지원**: 다양한 언어의 입력을 자동으로 감지하고 처리
- **모듈식 아키텍처**: 코어 시스템과 도메인별 에이전트로 구성된 유연한 설계
- **에이전트 라우팅**: 적절한 전문 에이전트에 사용자 요청을 자동으로 라우팅
- **도구 통합**: 웹 검색, 코드 실행 등의 다양한 도구와 통합
- **AI 모델 활용**: Google Vertex AI의 최신 LLM 모델 활용

## 설치

```bash
# Poetry를 통한 설치
poetry install
```

## 시작하기

```bash
# ADK CLI 인터페이스 실행
adk run .

# 또는 웹 인터페이스 실행
adk web .
```

## 개발 환경 설정

```bash
# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 API 키 등을 설정

# 개발 의존성 설치
poetry install --with dev
```

## 라이선스

MIT 