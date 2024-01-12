import streamlit as st
from utils import write_message
from agent import generate_response, agent, kg_qa, memory
from datetime import datetime
from langchain.chains import RetrievalQA
from solutions.tools.vector import retriever
from langchain_community.callbacks import get_openai_callback
# from langchain.globals import set_debug
# from langchain.globals import set_verbose

# set_debug(True)
# set_verbose(True)

# tag::setup[]
# Page Config
st.set_page_config(
    page_title="RNS Buddy",
    page_icon=":newspaper:"
)
# end::setup[]

    
st.header("RNS buddy")

# tag::session[]
# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.clear()
    st.session_state.messages = [
            {"role": "assistant", "content": "Ask me anything about listed UK companies"},
        ]
# end::session[]

# tag::submit[]
# Submit handler
# Submit handler
def handle_submit(message):
    # Handle the response
    with st.spinner('Thinking...'):
        with get_openai_callback() as cb:
            response = generate_response(message)
            write_message('assistant', response)
            #  logging
            print("\nRESPONSE - ", end=' ')
            print(datetime.now())
            print("\n")
            print("Agent\n ")
            print(agent)
            print("\n")
            print("Response")
            print(retriever.get_relevant_documents(query=prompt))
            for doc in retriever.get_relevant_documents(prompt):
                print("-" * 80)
                print(doc)
            print("\n")
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
# end::submit[]

# tag::chat[]
# with st.container():
    # Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if prompt := st.chat_input("Ask away..."):
    # Display user message in chat message container
    write_message('user', prompt)

    # Generate a response
    handle_submit(prompt)

# end::chat[]

def on_reset_chat_button_click():
    print(agent.memory.chat_memory.messages)
    st.session_state.messages = []
    st.session_state.clear()
    memory.clear()
    print(agent.memory.chat_memory.messages)
    st.success("Chat is reset")

st.button("Reset chat", on_click=on_reset_chat_button_click)