import streamlit as st
from utils import write_message
from agent import generate_response, memory, agent_executor
from datetime import datetime
from solutions.tools.vector import retriever
from langchain_community.callbacks import get_openai_callback

from langchain.globals import set_debug

from langchain.globals import set_verbose

set_debug(True)
set_verbose(True)

# Page Config
st.set_page_config(page_title="RNS Buddy", page_icon=":newspaper:")


st.header("RNS buddy")


def write_message(role, content, save=True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        st.session_state.messages.append({"role": role, "content": content})

    # Write to UI
    with st.chat_message(role):
        st.markdown(content)


# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Ask me anything about listed UK companies rns news",
        },
    ]


# Submit handler
def handle_submit(message):
    # Handle the response
    with st.spinner("Thinking..."):
        with get_openai_callback() as cb:
            response = generate_response(message)
            write_message("assistant", response)

            #  logging
            # print("\nRESPONSE - ", end=" ")
            # print(datetime.now())
            # print("\n")
            # print("Agent\n ")
            # print(agent)
            # print("\n")
            # print("Response")
            # print(retriever.get_relevant_documents(query=prompt))
            # for doc in retriever.get_relevant_documents(prompt):
            #     print("-" * 80)
            #     print(doc)
            # print("\n")
            # print(f"Total Tokens: {cb.total_tokens}")
            # print(f"Prompt Tokens: {cb.prompt_tokens}")
            # print(f"Completion Tokens: {cb.completion_tokens}")
            # print(f"Total Cost (USD): ${cb.total_cost}")


# with st.container():
# Display messages in Session State
for message in st.session_state.messages:
    write_message(message["role"], message["content"], save=False)

# Handle any user input
if prompt := st.chat_input("Ask away..."):
    # Display user message in chat message container
    write_message("user", prompt)

    # Generate a response
    handle_submit(prompt)


def on_reset_chat_button_click():
    print(agent_executor.memory.chat_memory.messages)
    st.session_state.messages = []
    st.session_state.clear()
    memory.clear()
    print(agent_executor.memory.chat_memory.messages)
    st.success("Chat is reset")


st.button("Reset chat", on_click=on_reset_chat_button_click)
