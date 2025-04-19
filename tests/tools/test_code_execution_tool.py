# tests/tools/test_code_execution_tool.py
import pytest
from google.adk.tools import FunctionTool
from src.jarvis.tools.code_execution_tool import execute_python_code, code_execution_tool
# Import types needed for schema verification
# from google.genai.types import FunctionDeclaration, Schema as GenaiSchema, Type as GenaiType, Tool # Not needed for this test
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

# Mock data for AsyncDDGS (Keep this if other tests use it, otherwise remove)
# MOCK_SEARCH_RESULTS = [
#     {'title': 'Result 1', 'href': 'http://example.com/1', 'body': 'Snippet 1...'},
#     {'title': 'Result 2', 'href': 'http://example.com/2', 'body': 'Snippet 2...'},
# ]
# MOCK_EMPTY_RESULTS = []

def test_code_execution_tool_definition():
    """코드 실행 도구(code_execution_tool) 객체가 올바르게 정의되었는지 확인합니다."""
    assert isinstance(code_execution_tool, FunctionTool)
    assert code_execution_tool.name == "execute_python_code"
    assert code_execution_tool.description is not None and len(code_execution_tool.description) > 0
    # Check for the security warning removal/update in docstring (optional but good practice)
    assert "restrictedpython" in code_execution_tool.description
    assert "exec` function" not in code_execution_tool.description # Verify old warning is gone

# --- Tests for Basic Execution (using restrictedpython) ---

@pytest.mark.asyncio
async def test_execute_safe_code_success():
    """5.4: 제한된 실행 성공 테스트 - 안전한 코드가 성공적으로 실행되는지 확인."""
    code = "x = 10\ny = 20\nprint(x + y)"
    result = await execute_python_code(code)
    assert "Stdout:\n30" in result
    assert "Stderr:" not in result

@pytest.mark.asyncio
async def test_execute_code_with_stderr():
    """5.4: Stderr 캡처 테스트 (restrictedpython) - 표준 에러 출력이 캡처되는지 확인."""
    code = "import sys\nsys.stderr.write('This is an error message')"
    # Note: `import sys` might need to be explicitly allowed if not covered by defaults
    # For now, assume safe_builtins or similar allows basic sys access needed for stderr capture.
    # If this fails, we need to adjust _safe_globals in the tool.
    result = await execute_python_code(code)
    assert "Stderr:\nThis is an error message" in result
    assert "Stdout:" not in result

@pytest.mark.asyncio
async def test_execute_no_output_code():
    """5.4: 출력 없는 코드 테스트 (restrictedpython) - 출력 없는 코드가 성공 메시지를 반환하는지 확인."""
    code = "a = 1\nb = 2"
    result = await execute_python_code(code)
    assert result == "Code executed successfully with no output."

# --- Tests for RestrictedPython Enforcement ---

@pytest.mark.asyncio
async def test_execute_disallowed_builtin_open():
    """5.4: 제한된 내장 함수 사용 불가 테스트 (open) - open 함수 사용 시 오류 반환 확인."""
    code = "f = open('myfile.txt', 'w')\nf.write('hello')\nf.close()"
    result = await execute_python_code(code)
    assert "Execution Error: Use of disallowed name or function: open" in result

@pytest.mark.asyncio
async def test_execute_disallowed_import_os():
    """5.4: 제한된 모듈 임포트 불가 테스트 (os) - os 모듈 임포트 시 오류 반환 확인."""
    code = "import os\nprint(os.getcwd())"
    result = await execute_python_code(code)
    # The specific error might vary slightly depending on restrictedpython version/config
    # It often manifests as a SyntaxError during compilation phase for imports
    assert ("Syntax Error:" in result or "ImportError:" in result or "disallowed module" in result)

@pytest.mark.asyncio
async def test_execute_disallowed_attribute_access():
    """Test accessing potentially unsafe attributes (e.g., __globals__)."""
    code = "def x(): pass\nprint(x.__globals__)" 
    result = await execute_python_code(code)
    # RestrictedPython should prevent access to sensitive attributes
    assert "Error during execution:" in result or "restricted" in result.lower()

# --- Tests for Error Handling (within restrictedpython) ---

@pytest.mark.asyncio
async def test_execute_syntax_error():
    """5.4: 제한된 컴파일 오류 테스트 (SyntaxError) - 구문 오류 시 컴파일 단계에서 오류 반환 확인."""
    code = "print('hello\""
    result = await execute_python_code(code)
    assert "Syntax Error:" in result
    # Check for specific message if consistent across versions
    # assert "(<inline code>, line 1)" in result

@pytest.mark.asyncio
async def test_execute_runtime_error_zero_division():
    """5.4: 제한된 런타임 오류 테스트 (ZeroDivisionError) - 허용된 연산 내 런타임 오류 처리 확인."""
    code = "print(1 / 0)"
    result = await execute_python_code(code)
    assert "Error during execution: division by zero" in result
    assert "Traceback:" not in result # Ensure traceback is not included by default


# --- Test Registration (Keep if applicable) ---
def test_code_execution_tool_registration():
    """코드 실행 도구가 tools/__init__.py의 available_tools 리스트에 등록되었는지 확인합니다."""
    from src.jarvis.tools import available_tools, code_execution_tool
    assert code_execution_tool in available_tools 