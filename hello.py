import pathlib
import shutil
from phi.tools import Toolkit
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.file import FileTools
from phi.utils.log import logger

web_agent = Agent(
    name="Code Generator",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=["Always include sources"],
    show_tool_calls=True,
    markdown=True,
    add_history_to_messages=True
)
web_agent.print_response(
    """
Die Bäume im Ofen lodern.
Die Vögel locken am Grill.
Die Sonnenschirme vermodern.
Im übrigen ist es still.

Es stecken die Spargel aus Dosen
Die zarten Köpfchen hervor.
Bunt ranken sich künstliche Rosen
In Faschingsgirlanden empor.

Ein Etwas, wie Glockenklingen,
Den Oberkellner bewegt,
Mir tausend Eier zu bringen,
Von Osterstören gelegt.

Ein süßer Duft von Havanna
Verweht in ringelnder Spur.
Ich fühle an meiner Susanna
Erwachende neue Natur.

Es lohnt sich manchmal, zu lieben,
Was kommt, nicht ist oder war.
Ein Frühlingsgedicht, geschrieben
Im kältesten Februar…
""",
    stream=True,
)

web_agent.print_response("Wer lockt am Grill?")
