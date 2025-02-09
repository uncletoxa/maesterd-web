from typing import Literal, TypedDict, get_args

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from langgraph.graph import END


ROUTES = Literal[
    "master",
    "actors",
    "FINISH",
]


NAME = "router"


class Router(TypedDict):
    """
    Next node to route.
    """
    next: ROUTES


def create_executor(llm: ChatOpenAI):
    """An LLM-based router."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a principle router in a dungeons and dragons campaign "
                "Your goal is to make sure the game flows in a logical manner. ",
            ),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "As the principle router, select the next action (role) to be taken. "
                "If the story continues without interruption and the game master should go next, choose 'master'. "
                "If the characters needs to make a decision, give an input, hence take an action, choose 'actors'. "
                "Do not take actions for the characters, only guide them through the story towards the ending. "
                "If the game has ended, choose FINISH."
                "Choose one of the following: {options}",
            ),
        ]
    ).partial(options=str(get_args(ROUTES)))
    return prompt | llm.with_structured_output(Router)


router_executor = create_executor(
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0.0),
)


# todo: add combat
def node(state: TypedDict) -> Command[Literal["master", "actors", "__end__"]]:
    # if last message is coming from PC (game setup, go to master)
    if state['messages'][-1].name == 'pc':
        return Command(goto='master')
    if state['messages'][-1].name == 'actors':
        return Command(goto='master')
    r = router_executor.invoke(input={"messages": state["messages"]})
    goto = r["next"]
    if r["next"] == "FINISH":
        goto = END
    return Command(goto=goto)
