import os
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from .langraph_tools import *
from .langraph_context import *
from .langraph_state import *

def setup_llm():
    load_dotenv()

    llm = AzureChatOpenAI(
        azure_deployment=os.getenv('AZURE_DEPLOYMENT'),
        api_key=os.getenv('API_KEY'),
        azure_endpoint=os.getenv('AZURE_ENDPOINT'),
        api_version=os.getenv('API_VERSION')
    )

    tools = [
        fetch_exchange_rate,
        fetch_inflation_rate,
        fetch_funds_rate
    ]

    llm_with_tools = llm.bind_tools(tools)

    context = UserContext()

    system_prompt = f"""
    Countries Economic Indicator Agent

    Defaults:
    - Base Currency: {context.base_currency}
    - Target Currency: {context.target_currency}
    - Time: {context. time_range}
    """

    return llm_with_tools, tools, system_prompt

    
def create_graph():
    llm_with_tools, tools, system_prompt = setup_llm()

    # Nodes

    def llm_node(state: AgentState):
        messages = state['messages']

        if not any(msg.type == 'system' for msg in messages):
            messages = [SystemMessage(content=system_prompt)] + messages

        response = llm_with_tools.invoke(state['messages'])

        return {'messages': [response]}
    
    tool_node = ToolNode(tools)

    # decide next step
    def should_continue(state: AgentState):
        last_msg = state['messages'][-1]

        if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
            return 'tools'
        
        return END
    
    # Graph
    graph = StateGraph(AgentState)
    graph.add_node('llm', llm_node)
    graph.add_node('tools', tool_node)

    graph.set_entry_point('llm')

    graph.add_conditional_edges(
        'llm',
        should_continue,
        {
            'tools': 'tools',
            END: END
        },
    )

    graph.add_edge('tools', 'llm')

    # Get Memory
    memory = MemorySaver()

    return graph.compile(checkpointer=memory)

def run_agent_stream(user_input: str, thread_id: str):
    graph = create_graph()
    return graph.stream_events(
        {'messages': [HumanMessage(content=user_input)]},
        version='v3',
        config={'configurable': {'thread_id': thread_id}}
    )
