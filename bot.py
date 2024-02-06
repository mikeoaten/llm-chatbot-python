"""
This module, `bot.py`, is responsible for the user interface and interaction of the RNS Buddy 
chatbot. It uses the Streamlit library to create a web-based interface for the chatbot.

The  chatbot's responses are generated using the `generate_response` function imported from the 
`agent` module. The module also contains a helper function `write_message` that saves a message 
to the session state and writes a message to the UI.

This module is part of the RNS Buddy project and is used for interacting with the user, generating
responses, and displaying relevant documents.
"""

from datetime import datetime
import json

import graphviz
import streamlit as st
from langchain.globals import set_debug

# from langchain.globals import set_verbose

from agent import generate_response, memory, agent_executor
from tools.vector import retriever


set_debug(True)
# set_verbose(True)

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
    """
    This function handles the submission of user messages and generates a response.
    It also retrieves relevant documents and displays them in the UI.
    """
    # Handle the response
    with st.spinner("Thinking..."):
        response = generate_response(message)

        results = retriever.get_relevant_documents(query=prompt)
        results_json = [result.to_json() for result in results]

        metadata_values = [
            {
                key: result_json.get("kwargs", {}).get("metadata", {}).get(key)
                for key in ["company", "url"]
            }
            for result_json in results_json
        ]

        metadata_values_str = [
            json.dumps(metadata, indent=4) for metadata in metadata_values
        ]

        metadata_values_str_combined = "\n\n".join(metadata_values_str)

        write_message(
            "assistant",
            response
            + "\n\n"
            + "Relevant documents:"
            + "\n\n"
            + metadata_values_str_combined
            + "\n\n"
            + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # Create a Graphviz graph
        dot = graphviz.Digraph(comment="Graph")

        top_result_json = None

        if results_json:
            top_result_json = results_json[0]

        if top_result_json:
            data = top_result_json.get("kwargs", {}).get("metadata", {}).get("graph")

            for item in data:
                if len(item) == 6:  # Assuming each item has 6 elements
                    (
                        node_from_id,
                        node_from_label,
                        node_to_id,
                        edge_label,
                        node_to_id,
                        node_to_label,
                    ) = item

                    # Add nodes and edges to the graph
                    dot.node(str(node_from_id), label=str(node_from_label))
                    dot.node(str(node_to_id), label=str(node_to_label))
                    dot.edge(str(node_from_id), str(node_to_id), label=str(edge_label))

        st.graphviz_chart(dot)


# with st.container():
# Display messages in Session State
for this_message in st.session_state.messages:
    write_message(this_message["role"], this_message["content"], save=False)

# Handle any user input
if prompt := st.chat_input("Ask away..."):
    # Display user message in chat message container
    write_message("user", prompt)

    # Generate a response
    handle_submit(prompt)


def on_reset_chat_button_click():
    """
    This function handles the reset of the chat.
    It clears the session state, memory, and prints the chat messages.
    """
    print(agent_executor.memory.chat_memory.messages)
    st.session_state.messages = []
    st.session_state.clear()
    memory.clear()
    print(agent_executor.memory.chat_memory.messages)
    st.success("Chat is reset")


st.button("Reset chat", on_click=on_reset_chat_button_click)
