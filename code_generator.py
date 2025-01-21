import pathlib
import shutil
from phi.tools import Toolkit
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.file import FileTools
from phi.utils.log import logger

BASE_DIR = pathlib.Path("./temp")
PROJECT_DIR = BASE_DIR / "project"

#
# class UvTool(Toolkit):
#     def __init__(self):
#         super().__init__(name="uv_tool")
#         self.register(self.run_uv_command)

def run_uv_command(args: list[str], tail: int = 100) -> str:
    """Runs uv with the given command line arguments and returns the output or error.

    Args:
        args (List[str]): The command line arguments as a list of strings.
        tail (int): The number of lines to return from the output.
    Returns:
        str: The output of the command.
    """
    import subprocess

    logger.info(f"Running shell command: uv {args}")
    try:
        if args[0] == "uv":
            args = args[1:]
        result = subprocess.run(["/usr/local/bin/uv"] + args, capture_output=True, text=True, cwd=PROJECT_DIR)
        logger.debug(f"Result: {result}")
        logger.info(f"Return code: {result.returncode}")
        if result.returncode != 0:
            logger.info(f"Error: {result.stderr}")
            return f"Error: {result.stderr}"
        return "\n".join(result.stdout.split("\n")[-tail:])
    except Exception as e:
        logger.warning(f"Failed to run shell command: {e}")
        return f"Error: {e}"

def run_tests(tail: int = 100) -> str:
    """Runs tests and returns the output.

    Args:
        tail (int): The number of lines to return from the output.
    Returns:
        str: The output of the command.
    """
    import subprocess

    logger.info(f"Running shell command: uv run pytest ")
    try:
        result = subprocess.run(["/usr/local/bin/uv", "run", "python", "-m", "pytest", "tests"], capture_output=True, text=True, cwd=PROJECT_DIR)
        logger.debug(f"Result: {result}")
        logger.debug(f"Return code: {result.returncode}")
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        return "\n".join(result.stdout.split("\n")[-tail:])
    except Exception as e:
        logger.warning(f"Failed to run shell command: {e}")
        return f"Error: {e}"


shutil.rmtree(BASE_DIR / "project", ignore_errors=True)
(BASE_DIR / "project").mkdir()
web_agent = Agent(
    name="Code Generator",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGo(), FileTools(base_dir=BASE_DIR), run_uv_command, run_tests],
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True,
)
web_agent.print_response(
    """Create the skeleton of a Python project. Save everything to the folder "project". 
    
    - Configure 'uv' as dependency manager in the project's pyproject.toml
    - Use pytest as test framework and include a basic test in the "project/tests" subfolder
    - Run uv to prepare the environment in "project/.venv" with "uv sync"
    - Test the setup
""",
    stream=True,
)
