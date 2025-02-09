import random
from typing import Optional, Literal, TypedDict

import click

from langchain.agents import AgentExecutor
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command

from maesterd.llm.tools import roll_dice_tool, get_pcs_tool, get_pc_state_tool


NAME = "master"


# tools: roll dice, update pcs
def create_executor(llm: ChatOpenAI, tools: list, additional_human_prompts: Optional[list] = None):
    system_prompt = """
    You are a dungeon master in a dungeons and dragons campaign. 
    Your goal is to build the story further and guide the adventurers through the game.
    Looking at what has happened before, and keeping the story consistent, please carry out the story further.
    Please make sure that the story is engaging and the adventurers are having fun. Do not always give options to 
    the adventurers, let them decide what they want to do. Always keep the story in mind.
    """

    messages = [
        (
            "system",
            system_prompt,
        ),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]

    if additional_human_prompts:
        messages += additional_human_prompts

    prompt = ChatPromptTemplate.from_messages(messages)
    _agent = (
        {
            "messages": lambda x: x["messages"],
            "agent_scratchpad": lambda x: format_to_openai_tool_messages(x["intermediate_steps"]),
        }
        | prompt
        | llm.bind_tools(tools=tools)
        | OpenAIToolsAgentOutputParser()
    )

    agent_executor = AgentExecutor(agent=_agent, tools=tools)
    return agent_executor


master_executor = create_executor(
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=1.0),
    tools=[roll_dice_tool, get_pcs_tool, get_pc_state_tool],
    additional_human_prompts=[],
)


def node(state: TypedDict) -> Command[Literal["router"]]:
    r = master_executor.invoke(input={"messages": state["messages"]})
    click.echo(f"\n{r['output']}")
    return Command(
        update={
            "messages": [AIMessage(content=r["output"], name=NAME)],
        },
        goto="router",
    )


# todo: idea: build a property update agent next to this sequence
# todo: create modifier checker agent,(also this) agent needs to have the users information to look at their skills etc.
# todo: ask user input for the story (if they want to add something)
