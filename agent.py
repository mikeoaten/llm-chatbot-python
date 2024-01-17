# https://github.com/neo4j-graphacademy/llm-chatbot-python/commit/bc521bcddd6c5298365bf14d91d534afb5c4c46b

from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from llm import llm
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.tools import Tool
from solutions.tools.vector import kg_qa
from solutions.tools.cypher import cypher_qa

import json

tools = [
    Tool.from_function(
        name="General Chat",
        description="For general chat not covered by other tools",
        func=llm.invoke,
        return_direct=True,
    ),
    Tool.from_function(
        name="Cypher QA",  # (1)
        description="Provides information about company news using Cypher",  # (2)
        func=cypher_qa,  # (3)
        return_direct=True,
    ),
    Tool.from_function(
        name="Vector Search Index",
        description="Provides information about company news using Vector Search",
        func=kg_qa,
        return_direct=True,
    ),
]


memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,
    return_messages=True,
)

agent_prompt = hub.pull("hwchase17/react-chat")
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)


def generate_response(prompt):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """
    response = agent_executor.invoke({"input": prompt})

    return response["output"]


print(agent_prompt)
