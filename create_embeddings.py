# https://neo4j.com/developer-blog/neo4j-langchain-vector-index-implementation/
# https://api.python.langchain.com/en/latest/vectorstores/langchain_community.vectorstores.neo4j_vector.Neo4jVector.html#

import streamlit as st
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from llm import embeddings

# Set variables for Neo4j driver
secrets = "secrets.toml"
uri = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]

neo4j_vector = Neo4jVector.from_existing_graph(
    embeddings,
    url=uri,
    username=username,
    password=password,
    database="neo4j",  # neo4j by default
    index_name="news_headline_embedding",  # vector by default
    node_label="News",  # Chunk by default
    text_node_properties=["headline_name"],  # text by default
    embedding_node_property="headline_name_embedding",  # embedding by default
)
