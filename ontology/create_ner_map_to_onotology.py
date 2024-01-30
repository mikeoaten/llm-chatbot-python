"""
This module is responsible for creating a mapping between the
extracted named entities from news articles and the ontology in
a Neo4j database. It uses the OpenCalais API to extract named
entities from the news articles and then creates relationships
between the extracted entities and the ontology nodes in the
Neo4j database.
"""
import logging
import requests
import streamlit as st
from neo4j import GraphDatabase

# --------------------------------------------
# Read data from the Neo4j database

# Set variables for Neo4j driver
uri = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]


# Define the query to read the news body from the database
def read_news_body(tx):
    """
    Read the news body from the database.

    Parameters:
    - tx: The transaction object for database operations.
    - body: The body of the news.
    - id: The ID of the news body.

    Returns:
    - A list containing the news ID and body.
    """
    result = tx.run("MATCH (n:News WHERE n.body IS NOT NULL) RETURN n.id, n.body")
    return [(record["n.body"], record["n.id"]) for record in result]


# Create the driver instance
driver = None
try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    driver.verify_connectivity()
    with driver.session() as session:
        results = session.execute_read(read_news_body)

except Exception as e:
    logging.error(f"Failed to create Neo4j driver: {e}")

# Close the driver instance
driver.close()

# print(results)


# --------------------------------------------
# Open Calais API

# Set variables for OpenCalais API key
api_key = st.secrets["OPENCALAIS_API_KEY"]


# Define the function to make the API call
def make_api_call(api_key, body):
    """
    Makes an API call to the Refinitiv PermID service.

    Args:
        api_key (str): The API key for authentication.
        body (str): The body of the request.

    Returns:
        requests.Response: The API response object.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the API call.
    """
    # Define the URL
    url = "https://api-eit.refinitiv.com/permid/calais?outputFormat=xml/rdf"

    # Encode the body as UTF-8
    body = body.encode("utf8")

    # Define the headers
    headers = {
        "x-ag-access-token": api_key,
        "Content-Type": "text/raw",
        # "x-calais-selectiveTags": "", #Optional
        "outputformat": "xml/rdf",
    }

    # Make the API call
    api_response = requests.post(url, headers=headers, data=body, timeout=80)

    return api_response


# Define the function to get the response text from the API call
def get_response_text(api_key, results):
    """
    Retrieves the response text from the API call for each result in the given list of results.

    Parameters:
    - api_key (str): The API key used for the API call.
    - results (list): The list of results containing the body and id.

    Returns:
    - str or None: The response text if the API call is successful, None otherwise.
    """
    for result in results:
        body, id = result

        # Make the API call
        response = make_api_call(api_key, body)

        if response.status_code == 200:
            print(response.text)

            return response.text

        else:
            logging.warning(
                f"Failed to retrieve data for newsId {id}. Status code: {response.status_code}"
            )

        # Break after the first API call
        # break

    return None


# --------------------------------------------
# Write the results to the Neo4j


def write_data(tx, response_text):
    """Write data to the ontology.

    Args:
        tx (Transaction): The Neo4j transaction object.
        response_text (str): The response text containing RDF/XML data.

    Returns:
        None
    """
    if response_text is not None:
        tx.run(
            "CALL n10s.rdf.import.inline($response_text, 'RDF/XML')",
            response_text=response_text,
        )
        print("Data imported successfully")
    else:
        print("Failed to import data")
    return


# Create the driver instance
driver = None
try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    driver.verify_connectivity()

    for result in results:
        response_text = get_response_text(api_key, [result])
        with driver.session() as session:
            results = session.execute_write(write_data, response_text)

except Exception as e:
    logging.error(f"Failed to create Neo4j driver: {e}")

# Close the driver instance
driver.close()

# --------------------------------------------
# Create relationships between the imported data and the ontology


# // Create MAPPED_TO relationships between the imported data and the ontology
# MATCH (m:Resource)
# WHERE m.uri STARTS //s.opencalais.com/1/type/em/e/'
# WITH 'http:
#  OR m.uri STARTS //s.opencalais.com/1/type/em/r/'
# WITH 'http:
#  OR m.uri STARTS //s.opencalais.com/1/type/er/'
# WITH 'http:
#  OR m.uri STARTS //s.opencalais.com/1/type/er/Geo/'
# WITH 'http:
# WITH m, split(m.uri, '/') AS parts
# MATCH (n)
# WHERE 'ns7__' + last(parts) IN labels(n)
#  OR 'ns5__' + last(parts) IN labels(n)
#  OR 'ns6__' + last(parts) IN labels(n)
#  OR 'ns8__' + last(parts) IN labels(n)
# MERGE (n)-[:MAPPED_TO]->(m)
# RETURN
# m, n;

# // Created MATCHED_TO relationships between rns Companies and Open Calais Compnaies
# MATCH (c1:Company)
# MATCH (c2: ns6__Company)
# WHERE c1.tidm = c2.ns0__ticker
# MERGE (c1)-[:MATCHED_TO]->(c2);
