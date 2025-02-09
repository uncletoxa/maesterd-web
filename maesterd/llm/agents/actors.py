import click
from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage
from langgraph.types import Command


NAME = "actors"


def node(state: TypedDict) -> Command[Literal["router"]]:
    r = click.prompt("What do you do? ")
    return Command(
        update={"messages": [HumanMessage(content=r, name=NAME)]},
        goto="router",
    )
