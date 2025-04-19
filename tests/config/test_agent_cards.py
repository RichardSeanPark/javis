import json
import os
import pytest
from pathlib import Path

# 프로젝트 루트 디렉토리 기준으로 경로 설정
# (이 파일의 위치가 tests/config/ 이므로 두 단계 위로 올라가야 함)
PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
AGENT_CARDS_DIR = CONFIG_DIR / "agent_cards"

CODING_AGENT_CARD_PATH = AGENT_CARDS_DIR / "coding_agent_card.json"
QA_AGENT_CARD_PATH = AGENT_CARDS_DIR / "qa_agent_card.json"

# Agent Card에 필수적으로 포함되어야 하는 최상위 키 목록
# common.types.AgentCard 모델을 기반으로 하되, Optional 필드는 제외할 수 있음
# 여기서는 예시로 주요 필수/핵심 필드만 검증
REQUIRED_AGENT_CARD_KEYS = ["name", "description", "url", "version", "capabilities", "skills"]


@pytest.fixture(scope="module")
def agent_cards_dir_exists():
    """Agent cards 디렉토리가 존재하는지 확인하는 픽스처"""
    assert AGENT_CARDS_DIR.exists(), f"디렉토리가 존재하지 않습니다: {AGENT_CARDS_DIR}"
    assert AGENT_CARDS_DIR.is_dir(), f"경로가 디렉토리가 아닙니다: {AGENT_CARDS_DIR}"


def test_coding_agent_card_exists(agent_cards_dir_exists):
    """coding_agent_card.json 파일 존재 여부 테스트"""
    assert CODING_AGENT_CARD_PATH.exists(), f"파일이 존재하지 않습니다: {CODING_AGENT_CARD_PATH}"
    assert CODING_AGENT_CARD_PATH.is_file(), f"경로가 파일이 아닙니다: {CODING_AGENT_CARD_PATH}"


def test_qa_agent_card_exists(agent_cards_dir_exists):
    """qa_agent_card.json 파일 존재 여부 테스트"""
    assert QA_AGENT_CARD_PATH.exists(), f"파일이 존재하지 않습니다: {QA_AGENT_CARD_PATH}"
    assert QA_AGENT_CARD_PATH.is_file(), f"경로가 파일이 아닙니다: {QA_AGENT_CARD_PATH}"


def _validate_json_file(file_path: Path):
    """주어진 경로의 파일이 유효한 JSON인지, 필수 키를 포함하는지 검증하는 헬퍼 함수"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        pytest.fail(f"유효하지 않은 JSON 형식입니다: {file_path}\nError: {e}")
    except FileNotFoundError:
        pytest.fail(f"파일을 찾을 수 없습니다: {file_path}")
    except Exception as e:
        pytest.fail(f"파일 읽기 중 오류 발생: {file_path}\nError: {e}")

    assert isinstance(data, dict), f"JSON 최상위 구조가 객체가 아닙니다: {file_path}"

    # 필수 키 존재 여부 확인
    missing_keys = [key for key in REQUIRED_AGENT_CARD_KEYS if key not in data]
    assert not missing_keys, f"필수 키가 누락되었습니다: {missing_keys} in {file_path}"

    # 스킬 목록 유효성 검사 (선택적)
    assert 'skills' in data and isinstance(data['skills'], list), f"'skills' 필드가 없거나 리스트가 아닙니다: {file_path}"
    if data.get('skills'): # 스킬이 있는 경우
        for i, skill in enumerate(data['skills']):
            assert isinstance(skill, dict), f"'skills' 리스트의 {i}번째 요소가 객체가 아닙니다: {file_path}"
            assert 'id' in skill, f"Skill {i}에 'id' 필드가 없습니다: {file_path}"
            assert 'name' in skill, f"Skill {i}에 'name' 필드가 없습니다: {file_path}"

    return data # 추가 검증을 위해 파싱된 데이터 반환

def test_coding_agent_card_validity(agent_cards_dir_exists):
    """coding_agent_card.json 파일의 JSON 유효성 및 필수 키 포함 여부 테스트"""
    data = _validate_json_file(CODING_AGENT_CARD_PATH)
    # 추가적인 내용 검증 (예: name이 일치하는지)
    assert data.get('name') == "CodingAgent", f"Agent name 불일치: {CODING_AGENT_CARD_PATH}"

def test_qa_agent_card_validity(agent_cards_dir_exists):
    """qa_agent_card.json 파일의 JSON 유효성 및 필수 키 포함 여부 테스트"""
    data = _validate_json_file(QA_AGENT_CARD_PATH)
    # 추가적인 내용 검증 (예: name이 일치하는지)
    assert data.get('name') == "KnowledgeQA_Agent", f"Agent name 불일치: {QA_AGENT_CARD_PATH}" 