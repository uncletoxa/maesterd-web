from langgraph.graph import StateGraph, START
from langgraph.graph import MessagesState

from maesterd.llm.agents import master
from maesterd.llm.agents import router
from maesterd.llm.agents import actors
from maesterd.llm.agents import tale
from maesterd.llm.agents import pc


class State(MessagesState):
    num_pc: int


builder = StateGraph(State)

builder.add_edge(START, tale.NAME)
builder.add_node(tale.NAME, tale.node)
builder.add_node(pc.NAME, pc.node)
builder.add_node(master.NAME, master.node)
builder.add_node(router.NAME, router.node)
builder.add_node(actors.NAME, actors.node)

graph = builder.compile()
