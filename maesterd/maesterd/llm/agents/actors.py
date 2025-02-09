from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.types import Command
from langgraph.types import interrupt


NAME = "actors"


def node(state: TypedDict) -> Command[Literal["router"]]:  # noqa
    return Command(
        update={"messages": [HumanMessage(content=state['actor_prompts'][-1], name=NAME)]},
        goto="router",
    )
