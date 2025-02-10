import click
import random
from typing import Literal, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command

from maesterd.models.campaign import CampaignSetting
from maesterd.core.session import CampaignSession


NAME = "tale"


def create_executor(llm: ChatOpenAI):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a Dungeons and Dragons game master. "
                "Your goal is to create a story for the players to interact with. "
                "Please be as creative as possible and make sure the story is engaging. "
                "Please, create the world and set the scene for the players. ",
            )
        ]
    )
    chain = prompt | llm.with_structured_output(CampaignSetting)
    return chain


temperature = round(random.uniform(0.8, 1.1), 2)
tale_executor = create_executor(
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=temperature),
)


# combat rules are taken care by the master
def node(state: TypedDict) -> Command[Literal["pc"]]:
    r = tale_executor.invoke(input={"messages": state["messages"]})
    CampaignSession.add_campaign_setting(CampaignSetting(**r))  # add the campaign setting to the session
    content = """Name: {name}\nSetting: {setting}\nGoal: {goal}""".format(
        name=r.get("name"),
        setting=r.get("setting"),
        goal=r.get("goal")
    )
    message = AIMessage(content=content, name=NAME)
    click.echo(f"\n{content}")
    return Command(
        update={
            "messages": [message],
            **r,
        },
        goto="pc"
    )
