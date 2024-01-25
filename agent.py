# https://github.com/neo4j-graphacademy/llm-chatbot-python/commit/bc521bcddd6c5298365bf14d91d534afb5c4c46b

from langchain.agents import AgentExecutor, create_react_agent

from langchain import hub
from llm import llm
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.tools import Tool
from tools.vector import kg_qa
from tools.cypher import cypher_qa
from prompts import agent_prompt
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

tools = [
    Tool.from_function(
        name="Vector Search Index",
        description="Provides information about company news using Vector Search. Always use this tool before using Cypher QA tool.",
        func=kg_qa,
        return_direct=True,
    ),
    Tool.from_function(
        name="Cypher QA",
        description="Provides information about company news using Cypher. Only use this tool after using Vector Search Index tool.",
        func=cypher_qa,
        return_direct=True,
    ),
    Tool.from_function(
        name="General Chat",
        description="For general chat not covered by other tools",
        func=llm.invoke,
        return_direct=True,
    ),
]


memory = ConversationBufferWindowMemory(
    memory_key="chat_history",
    k=5,
    return_messages=True,
    Verbose=True,
)


def _handle_error(error) -> str:
    return str(error)[:50]


# agent_prompt = hub.pull("hwchase17/react-chat")
agent_prompt = agent_prompt
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    # handle_parsing_errors="If the error is Could not parse LLM output: `Do I need to use a tool? Yes` then use Vector Search Index tool",
    # handle_parsing_errors=False,
    handle_parsing_errors=_handle_error,
    # return_intermediate_steps=True,
)


def generate_response(prompt):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """
    response = agent_executor.invoke({"input": prompt})
    # return response["output"]

    output = response["output"]

    # Check the data type of output
    if isinstance(output, str):
        return output
    elif isinstance(output, dict):
        return output.get("result", "")
    else:
        return "Unexpected output format"
