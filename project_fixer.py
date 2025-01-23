import pathlib
import subprocess
from phi.agent import Agent
from phi.utils.log import logger
from phi.model.openai import OpenAIChat
from phi.tools.file import FileTools

PROJECT_DIR = pathlib.Path("./temp")

def run_analysis_tool(file_name: str=None) -> str:
    """Runs the analysis tool on the given project directory and returns the output.

    Args:
        file_name (str): Optional file name to limit the analysis on.
            This should only be used if the file_name is known and exists.
            Otherwise, leave it empty.

    Returns:
        str: The output of the analysis tool.
    """
    args = ["ruff", "check", "--select", "S", "--output-format", "json-lines"]
    if file_name:
        if pathlib.Path(file_name).is_absolute():
            target_file = pathlib.Path(file_name)
        else:
            target_file = PROJECT_DIR / file_name
        if PROJECT_DIR not in target_file.parents:
            return "Error: Access to this file is not allowed!"
        if not target_file.exists():
            return "Error: The target file does not exist!"
        args.append(target_file)
    try:
        logger.info(f"Running ruff check: {args}")
        result = subprocess.run(args, capture_output=True, text=True, cwd=PROJECT_DIR)
        logger.debug(f"Result: {result}")
        logger.debug(f"Return code: {result.returncode}")
        if result.returncode == 2:
            return f"Error: {result.stderr}"
        return result.stdout
    except Exception as e:
        logger.warning(f"Failed to run shell command: {e}")
        return f"Error: {e}"

def autofix(file_name: str=None) -> str:
    """Runs deterministic autofix tools.

    Args:
        file_name (str): Optional file name to limit the work on.
            This should only be used if the file_name is known and exists.
            Otherwise, leave it empty.

    Returns:
        str: The output of the analysis tool.
    """
    args = ["ruff", "check", "--fix"]
    if file_name:
        if pathlib.Path(file_name).is_absolute():
            target_file = pathlib.Path(file_name)
        else:
            target_file = PROJECT_DIR / file_name
        if PROJECT_DIR not in target_file.parents:
            return "Error: Access to this file is not allowed!"
        if not target_file.exists():
            return "Error: The target file does not exist!"
        args.append(target_file)
    try:
        logger.info(f"Running ruff fix: {args}")
        result = subprocess.run(args, capture_output=True, text=True, cwd=PROJECT_DIR)
        logger.debug(f"Result: {result}")
        logger.debug(f"Return code: {result.returncode}")
        if result.returncode == 2:
            return f"Error: {result.stderr}"
        return result.stdout
    except Exception as e:
        logger.warning(f"Failed to run shell command: {e}")
        return f"Error: {e}"

analysis_agent = Agent(
    name="Analyzer",
    role="Analyzes the project for any issue and outputs a list of issues.",
    tools=[run_analysis_tool],
    show_tool_calls=False,
    description="You are responsible for identifying issues in a software project with a linting tool",
    instructions="""Run the analysis tools and output a list of issues found. 
    The list should contain the exact file path, line number and position and a full description of the issues found.
    
    Always use the full absolute path of the files, never only the name.
    
    If you encounter any issues with the tools, please output the errors in detail.
    
    If (and only if) you're asked to return results for a single file, pass the relative path of the file to your tools."""
)
fixing_agent = Agent(
    name="Fixer",
    # model=OpenAIChat(id="gpt-4o-mini"),
    role="Takes one issue and fixes it in a software project.",
    tools=[FileTools(base_dir=PROJECT_DIR), autofix],
    show_tool_calls=True,
    description="You are responsible for fixing a given problem in a software project",
    instructions="""You are a very experienced, clean coder. 
    But you respect the style of the existing code and try to edit it in the existing style. 
    You thoroughly double-check if your fix really improves the situation. 
    If you assess, that there is a very good reason not to follow the suggestion, you disable the linting for this issue and add a comment why.
    
    To fix the issue, you can edit the file. 
    Make sure to modify the files in place.
    Always add a trailing newline to any text files you change.
    
    Always use the full absolute path of the files, never only the name.
    """
)
main_agent = Agent(
    name="Coordinator",
    # model=OpenAIChat(id="o1-mini"),
    model=OpenAIChat(id="gpt-4o"),
    reasoning=True,
    team=[analysis_agent, fixing_agent],
    tools=[FileTools(base_dir=PROJECT_DIR)],
    instructions=["""
    Analyze and apply fixes for issues in the given Python project.
    
    Always use the full absolute path of the files, never only the name.
    
    Start your job with running the analyis tool.
    Then try to fix the issues by running other tools.
    Afterwards always double-check if everything is resolved, otherwise re-iterate.
    That means, after fixing the files, run the analyzing tools again and see if further fixes are necessary.    
    """],
    show_tool_calls=True,
    markdown=True,
)
main_agent.print_response(
    "Run the analysis tool and fix everything it reports. ",
    stream=True,
)
