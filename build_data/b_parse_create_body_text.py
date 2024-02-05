"""
This module is designed to interact with a Neo4j database
to read and write data. 

It includes two main functions: `read_data` and `write_data`.
`read_data` reads news articles from the Neo4j database and
returns a list of these articles.
`write_data` writes the body text of a news article to the
corresponding node in the database.

The module first creates a driver instance to connect to the
Neo4j database. It then uses this driver to execute the
`read_data` function and store the results.

Next, it loops through the results. For each result, it parses
the HTML body of the news article, extracts the text, and cleans
it by removing certain separators and extra line breaks.

Finally, it creates another driver instance and uses it to execute
the `write_data` function, writing the cleaned text back to the
corresponding node in the database.

The module handles various exceptions that might occur during the
execution, such as service unavailability and authentication errors,
and logs these exceptions for debugging purposes.
"""

import json
import re
import logging
import streamlit as st

from bs4 import BeautifulSoup
from neo4j import GraphDatabase


# Set variables for Neo4j driver
SECRETS = "secrets.toml"
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
    read_data_result = tx.run(
        "MATCH (r:Rns WHERE r.news_article IS NOT NULL) RETURN r.news_article, r.id"
    )
    return [(record["r.news_article"], record["r.id"]) for record in read_data_result]


def write_data(tx):
    """
    Writes the body text of a news article to the corresponding node in the database.

    Args:
        tx: The transaction object used to execute the Cypher query.

    Returns:
        None
    """
    tx.run("MATCH (n:News WHERE n.id = $id) SET n.body = $text", id=id, text=text)


# Create the driver instance
DRIVER = None
try:
    DRIVER = GraphDatabase.driver(uri, auth=(username, password))
    DRIVER.verify_connectivity()
    with DRIVER.session() as session:
        results = session.execute_read(read_data)

except DRIVER.exceptions.ServiceUnavailable as e:
    logging.error("Failed to connect to Neo4j: %s", e)
except DRIVER.exceptions.AuthError as e:
    logging.error("Authentication error: %s", e)
except Exception as e:
    logging.error("An unexpected error occurred: %s", e)

# Close the driver instance
DRIVER.close()

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
    DRIVER = None
    try:
        DRIVER = GraphDatabase.driver(uri, auth=(username, password))
        DRIVER.verify_connectivity()
        with DRIVER.session() as session:
            session.execute_write(write_data)

    except DRIVER.exceptions.ServiceUnavailable as e:
        logging.error("Failed to connect to Neo4j: %s", e)
    except DRIVER.exceptions.AuthError as e:
        logging.error("Authentication error: %s", e)
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)

    # Close the driver instance
    DRIVER.close()

    # print(id)
    # print(text)
