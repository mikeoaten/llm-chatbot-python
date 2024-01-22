# https://neo4j.com/developer-blog/neo4j-langchain-vector-index-implementation/
# https://api.python.langchain.com/en/latest/vectorstores/langchain_community.vectorstores.neo4j_vector.Neo4jVector.html#

import sys

sys.path.append(r"C:\Users\mikej\Documents\GitHub\llm-chatbot-python")

import streamlit as st
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from llm import embeddings


# Set variables for Neo4j driver
secrets = "secrets.toml"
uri = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]

# Create embeddings for news headlines
Neo4jVector.from_existing_graph(
    embeddings,
    url=uri,
    username=username,
    password=password,
    database="neo4j",
    index_name="news_headline_embedding",
    node_label="News",
    text_node_properties=["headline_name"],
    embedding_node_property="headline_name_embedding",
)

# Create embeddings for news article body text
Neo4jVector.from_existing_graph(
    embeddings,
    url=uri,
    username=username,
    password=password,
    database="neo4j",
    index_name="news_body_embedding",
    node_label="News",
    text_node_properties=["body"],
    embedding_node_property="body_embedding",
)
