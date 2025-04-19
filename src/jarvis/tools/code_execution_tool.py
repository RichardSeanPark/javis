# src/jarvis/tools/code_execution_tool.py
import io
import logging
import contextlib
import traceback
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)

async def execute_python_code(code: str) -> str:
    """
    Executes the given Python code snippet and returns its output (stdout and stderr).

    **SECURITY WARNING:** This tool uses Python's `exec` function, which can be
    extremely dangerous if not used carefully. Executing untrusted code can lead
    to severe security vulnerabilities. For production environments, use a proper
    sandboxing mechanism like Docker containers or `restrictedpython`.

    Args:
        code: The Python code string to execute.

    Returns:
        A string containing the captured stdout and stderr from the executed code,
        or an error message if execution fails.
    """
    logger.info(f"Executing Python code:\n```python\n{code}\n```")
    # TODO: Implement secure sandboxing (e.g., Docker, restrictedpython) for production.
    local_vars = {}
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
            # Execute the code in a restricted namespace
            exec(code, {'__builtins__': __builtins__}, local_vars)

        stdout = stdout_capture.getvalue()
        stderr = stderr_capture.getvalue()

        output = ""
        if stdout:
            output += f"Stdout:\n{stdout}\n"
        if stderr:
            output += f"Stderr:\n{stderr}\n"

        if not output:
            output = "Code executed successfully with no output."

        logger.info("Code execution successful.")
        return output.strip()

    except Exception as e:
        logger.error(f"Error executing Python code: {e}", exc_info=True)
        # Capture traceback for detailed error reporting
        error_details = traceback.format_exc()
        return f"Error during execution:\n{e}\n\nTraceback:\n{error_details}"

# Create the ADK FunctionTool object
# The description will be taken from the function's docstring.
code_execution_tool = FunctionTool(func=execute_python_code)

# Example usage (for testing purposes)
async def main():
    # Example 1: Simple print
    result1 = await execute_python_code("print('Hello from exec!')")
    print(f"--- Result 1 ---\n{result1}\n------------------\n")

    # Example 2: Calculation
    result2 = await execute_python_code("x = 5 * 10\nprint(f'Result is {x}')")
    print(f"--- Result 2 ---\n{result2}\n------------------\n")

    # Example 3: Code with an error
    result3 = await execute_python_code("print(1 / 0)")
    print(f"--- Result 3 ---\n{result3}\n------------------\n")

    # Example 4: No output
    result4 = await execute_python_code("y = 10")
    print(f"--- Result 4 ---\n{result4}\n------------------\n")


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot run new event loop" in str(e):
            print("Cannot run example directly when an event loop is already running.")
        else:
            raise e 