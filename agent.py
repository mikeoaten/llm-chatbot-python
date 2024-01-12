from langchain.agents import AgentType, initialize_agent

# Include the LLM from a previous lesson
from llm import llm

from langchain.chains.conversation.memory import ConversationBufferWindowMemory

from langchain.tools import Tool

from solutions.tools.vector import kg_qa

from langchain.chains import GraphCypherQAChain
from graph import graph
from solutions.tools.cypher import cypher_qa

SYSTEM_MESSAGE = """
You are an expert company news analyst specialising in provding information from Regulatory News Service (RNS).

DO NOT answer questions using your pre-trained knowledge, only use the information provided in the context provided to you. This is very important, so before you make a response think if the information is only available in the context provided to you.

Do not answer any questions that do not relate to company news.
"""

memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True,
)

tools = [
    Tool.from_function(
        name="Vector Search Index",  # (1)
        description="Provides information from company news releases using Vector Search", # (2)
        func = kg_qa, # (3)
    ),
    Tool.from_function(
        name="Graph Cypher QA Chain",  # (1)
        description="Provides information about company news using graph database search", # (2)
        func = cypher_qa, # (3)
    )
]


agent = initialize_agent(
    tools,
    llm,
    memory=memory,
    verbose=True,
    return_source_documents=True,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    agent_kwargs={
        "system_message": SYSTEM_MESSAGE
        }
)

def generate_response(prompt):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """
    response = agent(prompt)

    return response['output']