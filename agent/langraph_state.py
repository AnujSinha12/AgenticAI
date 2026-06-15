from typing import List, TypedDict, Annotated
from langgraph.graph.message import add_messages

# State

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]