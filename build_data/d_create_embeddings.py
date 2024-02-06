"""
This module is used to create embeddings for split text from news articles. 

It imports necessary modules and adds a specific path to the system path list. 
Then, it sets up the variables for the Neo4j driver using secrets from a toml file.

Finally, it uses the `from_existing_graph` method from the `Neo4jVector` class 
to create embeddings from the existing graph. The embeddings are created for 
the 'SplitText' nodes in the 'neo4j' database, specifically for the 'split_text' 
property of these nodes. The resulting embeddings are stored in the 
'split_text_embedding' property of the nodes.
"""

import sys

# Add the path to the sys.path list
sys.path.append(r"C:\Users\mikej\Documents\GitHub\tikos-rns-demo")

import streamlit as st
from langchain_community.vectorstores.neo4j_vector import Neo4jVector

from llm import embeddings

# Set variables for Neo4j driver
SECRETS = "secrets.toml"
uri = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]


# Create embeddings for news article split text
Neo4jVector.from_existing_graph(
    embeddings,
    url=uri,
    username=username,
    password=password,
    database="neo4j",
    index_name="split_text_embedding",
    node_label="SplitText",
    text_node_properties=["split_text"],
    embedding_node_property="split_text_embedding",
)

print("Embeddings created")
