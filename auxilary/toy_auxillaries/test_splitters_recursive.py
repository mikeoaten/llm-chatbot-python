from langchain.text_splitter import RecursiveCharacterTextSplitter
from neo4j import GraphDatabase
import streamlit as st
import logging

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
        A list of news article bopdy text and ids.
    """
    result = tx.run("MATCH (n:News WHERE n.body IS NOT NULL) RETURN n.body, n.id")
    return [(record["n.body"], record["n.id"]) for record in result]


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

text_splitter = RecursiveCharacterTextSplitter(
    # Set a really small chunk size, just to show.
    chunk_size=300,
    chunk_overlap=60,
    length_function=len,
    is_separator_regex=False,
)

# Loop through results
for result in results:
    body, id = result
    texts = text_splitter.create_documents([body])

    # print(texts[0])
    # print(texts[1])
    # count the number of texts
    # print(len(texts))
    # print(texts)
    print("\n".join([str(text) for text in texts]))
    # convert the output to a jsonl file
    # with open("text.jsonl", "w") as f:
    #     f.write("\n".join([str(text) for text in texts]))
