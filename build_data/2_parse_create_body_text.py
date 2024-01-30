from bs4 import BeautifulSoup
from neo4j import GraphDatabase
import streamlit as st
import json
import re
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
        A list of news articles from the Neo4j database.
    """
    result = tx.run(
        "MATCH (r:Rns WHERE r.news_article IS NOT NULL) RETURN r.news_article, r.id"
    )
    return [(record["r.news_article"], record["r.id"]) for record in result]


def write_data(tx):
    """
    Writes the body text of a news article to the corresponding node in the database.

    Args:
        tx: The transaction object used to execute the Cypher query.

    Returns:
        None
    """
    tx.run("MATCH (n:News WHERE n.id = $id) SET n.body = $text", id=id, text=text)
    return


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
    html = data["body"]

    # Parse html file
    soup = BeautifulSoup(html, "html.parser")
    # Return all text elements
    text = soup.get_text()

    # Retain text before separators
    separators = [
        "- END -",
        "ENQUIRIES:",
        "This information is provided by RNS",
        "For further information",
    ]
    text_parts = [text]

    for x in separators:
        new_parts = []
        for part in text_parts:
            new_parts.extend(part.split(x))
        text_parts = new_parts

    # If there is text before a separators, take the first part, if not, take all text
    if len(text_parts) > 1:
        text = text_parts[0]
    else:
        text = text

    # Remove consecutive line breaks
    text = re.sub("\n{2,}", "\n", text)
    # Remove all line breaks or spaces after the last text
    text = text.rstrip()

    # Create the driver instance
    driver = None
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        with driver.session() as session:
            session.execute_write(write_data)

    except Exception as e:
        logging.error(f"Failed to create Neo4j driver: {e}")

    # Close the driver instance
    driver.close()

    # print(id)
    # print(text)
