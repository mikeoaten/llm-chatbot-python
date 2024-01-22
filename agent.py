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
        name="General Chat",
        description="For general chat not covered by other tools",
        func=llm.invoke,
        return_direct=True,
    ),
    Tool.from_function(
        name="Cypher QA",
        description="Provides information about company news using Cypher",
        func=cypher_qa,
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
    Verbose=True,
)

# agent_prompt = hub.pull("hwchase17/react-chat")
agent_prompt = agent_prompt
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    # handle_parsing_errors="Check your output and make sure it conforms, so every AIMessage content includes Thought: Do I need to use a tool? Yes/No",
    handle_parsing_errors=True,
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


# for chunk in agent_executor.stream(
#     {"input": "using vector search name one rns headline"}
# ):
#     print(chunk)
#     print("------")


# while True:
#     q = input("> ")
#     print(agent_executor.invoke({"input": q}))
