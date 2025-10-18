from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END
from langgraph.graph.state import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
os.environ["LANGSMITH_API_KEY"]=os.getenv("LANGSMITH_API_KEY")

class State(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

model=ChatOpenAI(temperature=0)

def make_default_graph():
    graph_workflow=StateGraph(State)
    

    def call_model(state):
        return {"messages" [model.invoke(state['messages'])]}
    
    graph_workflow.add_node("agent",call_model)
    graph_workflow.add_edge("agent",END)
    graph_workflow.add_edge(START,"agent")
    agent=graph_workflow.compile()
    return agent

agent=make_default_graph()

