from langchain import hub

model_list = [
    "openai-tools-agent",
    "react-chat-json",
    "structured-chat-agent",
    "react-chat",
    "self-ask-with-search",
]

for model in model_list:
    agent_prompt = hub.pull(f"hwchase17/{model}")
    print("------------------------------")
    print(model)
    print(agent_prompt)
    print("------------------------------")
