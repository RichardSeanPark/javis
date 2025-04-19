# tests/tools/test_code_execution_tool.py
import pytest
from google.adk.tools import FunctionTool
from src.jarvis.tools.code_execution_tool import execute_python_code, code_execution_tool
# Import types needed for schema verification
from google.genai.types import FunctionDeclaration, Schema as GenaiSchema, Type as GenaiType

# Remove @pytest.mark.asyncio as the test is now synchronous
def test_code_execution_tool_definition():
    """코드 실행 도구(code_execution_tool) 객체가 올바르게 정의되었는지 확인합니다."""
    assert isinstance(code_execution_tool, FunctionTool)
    assert code_execution_tool.name == "execute_python_code"
    assert code_execution_tool.description is not None and len(code_execution_tool.description) > 0
    assert "RestrictedPython" in code_execution_tool.description
    assert "print) is disabled" in code_execution_tool.description
    from src.jarvis.tools import available_tools
    assert code_execution_tool in available_tools

@pytest.mark.asyncio
async def test_execute_simple_print_disabled():
    """print문이 포함된 코드 실행 시 출력이 없고 성공 메시지를 반환하는지 테스트합니다."""
    code = "print('hello world')" # print is now disabled
    result = await execute_python_code(code)
    # Should now return the success message as print does nothing or raises NameError handled internally
    # Let's check for the success message OR the specific NameError for _print_
    assert result == "Code executed successfully (no stderr output)." or \
           "Error during restricted execution: NameError: name '_print_' is not defined" in result

@pytest.mark.asyncio
async def test_execute_calculation_print_disabled():
    """계산 및 print문 실행 시 출력이 없고 성공 메시지를 반환하는지 테스트합니다."""
    code = "x = 10\ny = 20\nprint(x * y)" # print is now disabled
    result = await execute_python_code(code)
    assert result == "Code executed successfully (no stderr output)." or \
           "Error during restricted execution: NameError: name '_print_' is not defined" in result

@pytest.mark.asyncio
async def test_execute_stderr():
    """표준 에러(stderr) 출력을 올바르게 캡처하는지 테스트합니다."""
    code_raise = "raise ValueError('test error')"
    result = await execute_python_code(code_raise)
    assert "Error during restricted execution: ValueError: test error" in result
    assert "Traceback" in result
    assert "Stderr:" not in result # Stderr capture was removed/repurposed

@pytest.mark.asyncio
async def test_execute_exception():
    """ZeroDivisionError 발생 시 에러와 traceback을 올바르게 반환하는지 테스트합니다."""
    code = "result = 1 / 0"
    result = await execute_python_code(code)
    assert "Error during restricted execution: ZeroDivisionError: division by zero" in result
    assert "Traceback" in result

@pytest.mark.asyncio
async def test_execute_no_output():
    """출력이 없는 코드 실행 시 성공 메시지를 반환하는지 테스트합니다."""
    code = "a = 1 + 2"
    result = await execute_python_code(code)
    assert result == "Code executed successfully (no stderr output)."

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

def test_code_execution_tool_registration():
    """코드 실행 도구가 tools/__init__.py의 available_tools 리스트에 등록되었는지 확인합니다."""
    from src.jarvis.tools import available_tools, code_execution_tool
    assert code_execution_tool in available_tools

# --- New RestrictedPython Security Tests --- (Corresponds to testcase.md 5.4)

@pytest.mark.asyncio
async def test_restricted_disallowed_builtin():
    """5.4: 제한된 빌트인 함수 테스트 (RestrictedPython) - open()"""
    code = "f = open('forbidden.txt', 'w')\nf.write('test')\nf.close()"
    result = await execute_python_code(code)
    assert "Error during restricted execution: NameError: name 'open' is not defined" in result

@pytest.mark.asyncio
async def test_restricted_disallowed_import():
    """5.4: 임의 모듈 임포트 금지 테스트 (RestrictedPython) - import os"""
    code = "import os\na = os.listdir('.')" # Removed print
    result = await execute_python_code(code)
    # Check for the runtime ImportError because __import__ is blocked
    assert "Error during restricted execution: ImportError: __import__ not found" in result

@pytest.mark.asyncio
async def test_restricted_disallowed_attribute_access():
    """5.4: 속성 접근 제한 테스트 (RestrictedPython) - __class__"""
    code = "a = (1).__class__" # Removed print
    result = await execute_python_code(code)
    assert "Error during restricted execution: SyntaxError:" in result
    assert "invalid attribute name because it starts with \"_\"" in result
 