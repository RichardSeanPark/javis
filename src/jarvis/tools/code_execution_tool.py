# src/jarvis/tools/code_execution_tool.py
import io
import logging
import contextlib
import traceback
import sys # For redirecting stderr as well
from google.adk.tools import FunctionTool
from restrictedpython import compile_restricted
from restrictedpython.Guards import safe_builtins, full_write_guard

logger = logging.getLogger(__name__)

# Define a safe environment for restricted execution
# Allow basic builtins, print, and math operations. Explicitly block dangerous ones.
_safe_globals = {
    '__builtins__': safe_builtins,
    '_print_': print, # Use _print_ name to potentially override behavior if needed
    '_getiter_': iter, # Needed for loops
    '_getattr_': getattr, # Often needed, consider security implications
    # Add other safe modules or functions here if necessary, e.g.:
    # 'math': math,
    # 'random': random,
}
_safe_globals['_write_'] = full_write_guard # Allow writing to objects (needed for print)

async def execute_python_code(code: str) -> str:
    """
    Executes the given Python code snippet in a restricted environment
    using `restrictedpython` and returns its output (stdout and stderr).

    Args:
        code: The Python code string to execute.

    Returns:
        A string containing the captured stdout and stderr from the executed code,
        or an error message if compilation or execution fails.
    """
    logger.info(f"Attempting to execute restricted Python code:\n```python\n{code}\n```")

    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    # Assign print to a key accessible within the restricted globals
    # Using 'print' directly relies on safe_builtins including it, which it does.
    # If we needed a custom printer: _safe_globals['print'] = lambda *args, **kw: print(*args, file=stdout_capture, **kw)
    local_vars = {} # Namespace for the executed code

    try:
        # Compile the code in restricted mode
        logger.debug("Compiling code in restricted mode...")
        byte_code = compile_restricted(
            code,
            filename='<inline code>',
            mode='exec'
        )
        logger.debug("Compilation successful.")

        # Execute the compiled code within the safe environment
        # Redirect stdout and stderr during execution
        with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
             logger.debug("Executing compiled code...")
             # Pass the safe globals and an empty local dict
             exec(byte_code, _safe_globals, local_vars)
             logger.debug("Execution finished.")

        stdout = stdout_capture.getvalue()
        stderr = stderr_capture.getvalue()

        output = ""
        if stdout:
            output += f"Stdout:\n{stdout}"
        if stderr:
            # Prepend newline if stdout exists for better formatting
            output += f"{'\n' if stdout else ''}Stderr:\n{stderr}"

        if not output:
            output = "Code executed successfully with no output."

        logger.info("Restricted code execution successful.")
        return output.strip()

    except SyntaxError as se:
        logger.warning(f"Syntax error during restricted compilation: {se}")
        return f"Syntax Error: {se}"
    except NameError as ne:
        # NameErrors often indicate use of disallowed builtins/globals
        logger.warning(f"NameError during restricted execution (potential disallowed access): {ne}")
        return f"Execution Error: Use of disallowed name or function: {ne}"
    except Exception as e:
        logger.error(f"Error executing restricted Python code: {e}", exc_info=True)
        error_details = traceback.format_exc()
        # Avoid returning overly verbose tracebacks unless debugging
        # return f"Error during execution:\n{e}\n\nTraceback:\n{error_details}"
        return f"Error during execution: {e}"

# Create the ADK FunctionTool object
# The description will be taken from the function's docstring.
code_execution_tool = FunctionTool(func=execute_python_code)

# Example usage (for testing purposes)
async def main():
    # Example 1: Simple print
    print("--- Example 1: Simple Print ---")
    result1 = await execute_python_code("print('Hello from restricted exec!')")
    print(f"Result:\n{result1}\n{'-'*20}\n")

    # Example 2: Calculation
    print("--- Example 2: Calculation ---")
    result2 = await execute_python_code("x = 5 * 10\nprint(f'Result is {x}')")
    print(f"Result:\n{result2}\n{'-'*20}\n")

    # Example 3: Allowed builtin (e.g., len)
    print("--- Example 3: Allowed Builtin ---")
    result3 = await execute_python_code("print(len([1, 2, 3]))")
    print(f"Result:\n{result3}\n{'-'*20}\n")

    # Example 4: Disallowed import
    print("--- Example 4: Disallowed Import ---")
    result4 = await execute_python_code("import os\nprint(os.getcwd())")
    print(f"Result:\n{result4}\n{'-'*20}\n")

    # Example 5: Disallowed builtin function (e.g., open)
    print("--- Example 5: Disallowed Builtin ---")
    result5 = await execute_python_code("f = open('test.txt', 'w')\nf.write('test')\nf.close()")
    print(f"Result:\n{result5}\n{'-'*20}\n")
    
    # Example 6: Syntax Error
    print("--- Example 6: Syntax Error ---")
    result6 = await execute_python_code("print('Hello'")
    print(f"Result:\n{result6}\n{'-'*20}\n")
    
    # Example 7: Runtime Error (allowed operation)
    print("--- Example 7: Allowed Runtime Error ---")
    result7 = await execute_python_code("print(1 / 0)")
    print(f"Result:\n{result7}\n{'-'*20}\n")


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO) # Setup logging for example run
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot run new event loop" in str(e):
            print("Cannot run example directly when an event loop is already running.")
        else:
            raise e 