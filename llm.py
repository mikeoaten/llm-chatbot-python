"""
This module is used to set up and configure the OpenAI chat
and embeddings functionalities.

It imports necessary modules and sets up the OpenAI API key
and model from a secrets file.

The `ChatOpenAI` class is instantiated with the OpenAI API key,
model, and a temperature of 0. This sets up the chat functionality
with the specified model and API key.

The `OpenAIEmbeddings` class is also instantiated with the OpenAI
API key, a specific model ("text-embedding-3-small"), and a progress
bar. This sets up the embeddings functionality with the specified model
and API key, and enables a progress bar for tracking the process.
"""

import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

secrets = "secrets.toml"

llm = ChatOpenAI(
    openai_api_key=st.secrets["OPENAI_API_KEY"],
    model=st.secrets["OPENAI_MODEL"],
    temperature=0,
)

embeddings = OpenAIEmbeddings(
    openai_api_key=st.secrets["OPENAI_API_KEY"],
    # model="text-embedding-3-small",
    model="text-embedding-ada-002",
    show_progress_bar=True,
)
