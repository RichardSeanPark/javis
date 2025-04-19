# src/jarvis/tools/code_execution_tool.py
import io
import logging
import contextlib
import traceback
from google.adk.tools import FunctionTool
from RestrictedPython import compile_restricted, safe_builtins, utility_builtins
# from RestrictedPython.PrintCollector import PrintCollector # REMOVED

logger = logging.getLogger(__name__)

async def execute_python_code(code: str) -> str:
    """
    Executes the given Python code snippet in a restricted environment
    and returns any captured standard error output.
    Note: Standard output (print) is disabled for security.
    To get a result, assign it to a variable. The final state of
    variables is not directly returned, but errors during execution are.

    Uses RestrictedPython library to prevent unsafe operations.

    Args:
        code: The Python code string to execute.

    Returns:
        A string containing captured stderr or an error message.
        If execution is successful with no stderr, returns a success message.
    """
    logger.info(f"Attempting to execute restricted Python code (print disabled):\n```python\n{code}\n```")
    local_vars = {}  # Dictionary to store local variables
    # stdout_capture = io.StringIO() # REMOVED stdout capture
    stderr_capture = io.StringIO()
    output = ""

    # Define a safe dictionary for globals - NO print included
    restricted_globals = {
        "__builtins__": safe_builtins.copy(),
        **utility_builtins,
        # No 'print' or '_print_' key
    }

    try:
        logger.debug("Compiling code using compile_restricted...")
        byte_code = compile_restricted(
            code,
            filename='<string>',
            mode='exec' # Keep exec mode to allow statements
        )
        logger.debug("Code compiled successfully in restricted mode.")

        # Execute the compiled byte code, only redirecting stderr
        with contextlib.redirect_stderr(stderr_capture):
            logger.debug("Executing compiled code...")
            exec(byte_code, restricted_globals, local_vars)
            logger.debug("Code execution finished.")

        # stdout = stdout_capture.getvalue() # REMOVED
        stderr = stderr_capture.getvalue()

        # No stdout check anymore
        # if stdout:
        #     output += f"Stdout:\n{stdout}\n"
        if stderr:
            output += f"Stderr:\n{stderr}\n"

        if not output:
            # Modify success message as there's no stdout expected
            output = "Code executed successfully (no stderr output)."

        logger.info("Restricted code execution successful (no print). ")

    except Exception as e:
        logger.error(f"Error executing restricted Python code: {e}", exc_info=True)
        error_details = traceback.format_exc()
        output = f"Error during restricted execution: {type(e).__name__}: {e}\n\nTraceback (may be limited by sandbox):\n{error_details}"

    finally:
        # Ensure streams are closed
        # stdout_capture.close() # REMOVED
        stderr_capture.close()

    return output.strip()

# Create the ADK FunctionTool object
# The description will be taken from the function's docstring.
code_execution_tool = FunctionTool(func=execute_python_code)

# Example usage (for testing purposes)
async def main():
    # Example 1: Simple print (should work)
    print("--- Example 1: Simple Print ---")
    result1 = await execute_python_code("print('Hello from restricted env!')")
    print(f"{result1}\n------------------\n")

    # Example 2: Calculation (should work)
    print("--- Example 2: Calculation ---")
    result2 = await execute_python_code("x = 5 * 10\nprint(f'Result is {x}')")
    print(f"{result2}\n------------------\n")

    # Example 3: Allowed built-in (should work)
    print("--- Example 3: Allowed Built-in ---")
    result3 = await execute_python_code("print(abs(-10))")
    print(f"{result3}\n------------------\n")

    # Example 4: Disallowed operation - File I/O (should fail)
    print("--- Example 4: Disallowed File I/O ---")
    result4 = await execute_python_code("open('test.txt', 'w').write('test')")
    print(f"{result4}\n------------------\n")

    # Example 5: Disallowed import (should fail)
    print("--- Example 5: Disallowed Import ---")
    result5 = await execute_python_code("import os\nprint(os.listdir('.'))")
    print(f"{result5}\n------------------\n")

    # Example 6: Code with a standard error (should be caught)
    print("--- Example 6: Standard Error ---")
    result6 = await execute_python_code("print(1 / 0)")
    print(f"{result6}\n------------------\n")


if __name__ == "__main__":
    import asyncio
    # Configure basic logging for the example
    logging.basicConfig(level=logging.INFO)
    logger.info("Running code execution tool examples...")
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot run new event loop" in str(e):
            print("Cannot run example directly when an event loop is already running.")
        else:
            raise e 