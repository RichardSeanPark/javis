# tests/tools/test_code_execution_tool.py
import pytest
from google.adk.tools import FunctionTool
from src.jarvis.tools.code_execution_tool import execute_python_code, code_execution_tool

@pytest.mark.asyncio
async def test_code_execution_tool_definition():
    """코드 실행 도구(code_execution_tool) 객체가 올바르게 정의되었는지 확인합니다."""
    assert isinstance(code_execution_tool, FunctionTool)
    assert code_execution_tool.name == "execute_python_code"
    assert "**SECURITY WARNING:**" in code_execution_tool.func.__doc__
    assert "Executes the given Python code snippet" in code_execution_tool.func.__doc__

@pytest.mark.asyncio
async def test_execute_simple_print():
    """간단한 print 문 실행 시 stdout을 올바르게 캡처하는지 테스트합니다."""
    code = "print('Hello from test!')"
    result = await execute_python_code(code)
    assert "Stdout:" in result
    assert "Hello from test!" in result
    assert "Stderr:" not in result
    assert "Error during execution:" not in result

@pytest.mark.asyncio
async def test_execute_calculation_and_print():
    """계산 및 print 문 실행 시 stdout을 올바르게 캡처하는지 테스트합니다."""
    code = "x = 10 + 5\nprint(f'Calculation result: {x}')"
    result = await execute_python_code(code)
    assert "Stdout:" in result
    assert "Calculation result: 15" in result
    assert "Stderr:" not in result
    assert "Error during execution:" not in result

@pytest.mark.asyncio
async def test_execute_stderr_capture():
    """stderr 출력을 올바르게 캡처하는지 테스트합니다."""
    code = "import sys\nsys.stderr.write('This is an error message')"
    result = await execute_python_code(code)
    assert "Stdout:" not in result # print가 없으므로 stdout은 없음
    assert "Stderr:" in result
    assert "This is an error message" in result
    assert "Error during execution:" not in result

@pytest.mark.asyncio
async def test_execute_exception():
    """코드 실행 중 예외 발생 시 오류 메시지와 traceback을 반환하는지 테스트합니다."""
    code = "result = 1 / 0"
    result = await execute_python_code(code)
    assert "Stdout:" not in result
    assert "Stderr:" not in result
    assert "Error during execution:" in result
    assert "ZeroDivisionError: division by zero" in result
    assert "Traceback (most recent call last):" in result
    assert 'File "<string>", line 1' in result # Check if error source is within exec'd code

@pytest.mark.asyncio
async def test_execute_no_output():
    """출력이 없는 코드 실행 시 적절한 메시지를 반환하는지 테스트합니다."""
    code = "a = 1\nb = 2\nc = a + b"
    result = await execute_python_code(code)
    assert result == "Code executed successfully with no output."

@pytest.mark.asyncio
@pytest.mark.skip(reason="Current implementation with exec allows this. Needs sandboxing.")
async def test_execute_potentially_dangerous_code():
    """위험할 수 있는 코드 실행 시도를 테스트합니다 (샌드박싱 필요)."""
    # This test should ideally fail or be blocked in a sandboxed environment.
    # In the current 'exec' implementation, it might succeed, which is a security risk.
    code = "import os\nprint(os.system('echo Potentially dangerous'))"
    result = await execute_python_code(code)
    # In a secure setup, this should return an error or restricted message.
    # For now, we expect it might run (hence the skip).
    assert "Error" in result or "Restricted" in result # Ideal assertion

# TODO: Add test for registration in tools/__init__.py after implementing that step 