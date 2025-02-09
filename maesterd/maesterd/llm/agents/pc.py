from typing import Union, Type, TypedDict, List, Literal
from dataclasses import dataclass, field

import click

from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command

from maesterd.models.character import PC
from maesterd.core.session import CampaignSession
from maesterd.core.utils import pc_to_str


NAME = "pc"


@dataclass
class PCS:
    pcs: List[PC] = field(metadata={"description": "List of player characters participating in the campaign"})


def create_executor(llm: ChatOpenAI, character_model: Union[Type, BaseModel, TypedDict]):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a Dungeons and Dragons game master's helper. "
                "Your goal is to create characters for the game. "
                "Make sure that the characters you create fits in the story and are engaging. "
                "Here is the story so far: ",
            ),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Please create {num_pc} characters. ",
            )
        ]
    )
    chain = prompt | llm.with_structured_output(character_model)
    return chain


pc_executor = create_executor(llm=ChatOpenAI(model="gpt-4o-mini", temperature=1.0), character_model=PCS)


def node(state: TypedDict) -> Command[Literal["router"]]:
    pcs = pc_executor.invoke(input={"messages": state["messages"], "num_pc": state['num_pc']})
    messages = []
    for pc in pcs["pcs"]:
        CampaignSession.add_pcs(pc)
        messages.append(AIMessage(player_str := pc_to_str(pc), name=NAME))
        click.echo(f"\n{player_str}")
    return Command(
        update={"messages": messages},
        goto="router",
    )
