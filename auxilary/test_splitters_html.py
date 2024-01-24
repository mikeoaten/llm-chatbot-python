# HTMLHeaderTextSplitter

from langchain.text_splitter import HTMLHeaderTextSplitter
from neo4j import GraphDatabase
import streamlit as st
import logging
import json


# Set variables for Neo4j driver
secrets = "secrets.toml"
uri = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]


def read_data(tx):
    """
    Read data from Neo4j database.

    Args:
        tx: Neo4j transaction object.

    Returns:
        A list of news articles from the Neo4j database.
    """
    result = tx.run(
        "MATCH (r:Rns WHERE r.news_article IS NOT NULL) RETURN r.news_article, r.id"
    )
    return [(record["r.news_article"], record["r.id"]) for record in result]


# Create the driver instance
driver = None
try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    driver.verify_connectivity()
    with driver.session() as session:
        results = session.execute_read(read_data)

except Exception as e:
    logging.error(f"Failed to create Neo4j driver: {e}")

# Close the driver instance
driver.close()

# Loop through results
for result in results:
    news_article, id = result
    data = json.loads(news_article)
    html_string = data["body"]

    headers_to_split_on = [
        ("h1", "Header 1"),
        ("h2", "Header 2"),
        ("h3", "Header 3"),
    ]

    html_splitter = HTMLHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    html_header_splits = html_splitter.split_text(html_string)
    print(html_header_splits)

# ----------------------------
