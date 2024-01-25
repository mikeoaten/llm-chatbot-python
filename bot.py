import streamlit as st
from agent import generate_response, memory, agent_executor
from datetime import datetime
from tools.vector import retriever
import json
import graphviz

from langchain.globals import set_debug

# from langchain.globals import set_verbose

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
    # Handle the response
    with st.spinner("Thinking..."):
        response = generate_response(message)

        results = retriever.get_relevant_documents(query=prompt)
        results_json = [result.to_json() for result in results]

        metadata_values = [
            {
                key: result_json.get("kwargs", {}).get("metadata", {}).get(key)
                for key in ["company", "url", "graph"]
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

        graph = graphviz.Digraph(
            graph_attr={"size": "2.5,2.5", "rankdir": "LR"},
            engine="neato",
        )
        graph.edge("run", "intr")
        graph.edge("intr", "runbl")
        graph.edge("runbl", "run")
        graph.edge("run", "kernel")
        graph.edge("kernel", "zombie")
        graph.edge("kernel", "sleep")

        st.graphviz_chart(graph)

        # # Create a Graphviz graph
        # dot = graphviz.Digraph()
        # # Add nodes and edges based on the response
        # for item in response:
        #     dot.node(item['id'], item['label'])
        #     for child in item['children']:
        #         dot.edge(item['id'], child)

        # # Display the graph using Streamlit
        # st.graphviz_chart(dot.source)


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
