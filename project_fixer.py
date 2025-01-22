import pathlib
import subprocess
from phi.tools import Toolkit
from phi.agent import Agent
from phi.utils.log import logger
from phi.tools.file import FileTools

PROJECT_DIR = pathlib.Path("./temp")

def run_analysis_tool(file_name: str=None) -> str:
    """Runs the analysis tool on the given project directory and returns the output.

    Args:
        file_name (str): Optional file name (relative path) to limit the analysis on.
            This should only be used if the file_name is known and exists.
            Otherwise, leave it empty.

    Returns:
        str: The output of the analysis tool.
    """
    logger.info(f"Running analysis tool on: {PROJECT_DIR}")
    args = ["ruff", "check", "--output-format", "json-lines"]
    if file_name:
        target_file = PROJECT_DIR / file_name
        if PROJECT_DIR not in target_file.parents:
            return "Error: Access to this file is not allowed!"
        if not target_file.exists():
            return "Error: The target file does not exist!"
        args.append(target_file)
    try:
        result = subprocess.run(args, capture_output=True, text=True, cwd=PROJECT_DIR)
        print(result)
        logger.debug(f"Result: {result}")
        logger.debug(f"Return code: {result.returncode}")
        if result.returncode == 2:
            return f"Error: {result.stderr}"
        return result.stdout
    except Exception as e:
        logger.warning(f"Failed to run shell command: {e}")
        return f"Error: {e}"

def fix_issues(project_dir: pathlib.Path, issues: list[dict]) -> None:
    """Fixes the issues in the project files based on the analysis tool's output.

    Args:
        project_dir (pathlib.Path): Path to the project directory.
        issues (list[dict]): A list of issues to fix.
    """
    logger.info("Fixing issues in project files")
    # TODO: Implement issue fixing

analysis_agent = Agent(
    name="Analyzer",
    role="Analyzes the project for any issue and outputs a list of issues.",
    tools=[run_analysis_tool],
    show_tool_calls=False,
    description="You are responsible for identifying issues in a software project with a linting tool",
    instructions="""Run the analysis tools and output a list of issues found. 
    The list should contain the exact file names, line number and position and a full description of the issues found.
    
    If you encounter any issues with the tools, please output the errors in detail.
    
    If (and only if) you're asked to return results for a single file, pass the relative path of the file to your tools."""
)

main_agent = Agent(
    name="Project Fixer",
    team=[analysis_agent],
    tools=[FileTools(base_dir=PROJECT_DIR)],
    instructions=["Analyze and suggest fixes for issues in the given Python project."],
    show_tool_calls=True,
    markdown=True,
)


main_agent.print_response(
    "Go and give me suggestions",
    stream=True,
)
