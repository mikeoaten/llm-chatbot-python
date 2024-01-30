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


# Read the news body from the database
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


# Format the OpenCalais API call
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


# Loop through the results and make the OpenCalais API call
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
            return response.text

        else:
            logging.warning(
                f"Failed to retrieve data for newsId {id}. Status code: {response.status_code}"
            )

        # Optionally break after the first API call, useful for testing
        # break

    return None


# --------------------------------------------
# Write the results to Neo4j database


# Set variables for Neo4j driver
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


# Create the driver instance and write the data
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


def create_constraints(tx):
    """
    Create constraints if they do not exist.
    """
    tx.run(
        """CREATE CONSTRAINT tag_tag_name IF NOT EXISTS
        for (t:Tag) REQUIRE t.tag_name IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT person_person_name IF NOT EXISTS
        for (p:Person) REQUIRE p.person_name IS UNIQUE
        """
    )
    tx.run(
        """CREATE CONSTRAINT organisation_organisation_name IF NOT EXISTS
        for (o:Organisation) REQUIRE o.organisation_name IS UNIQUE
        """
    )
    tx.run(
        """CREATE CONSTRAINT industry_industry_name IF NOT EXISTS
        for (i:Industry) REQUIRE i.industry_name IS UNIQUE
        """
    )
    tx.run(
        """CREATE CONSTRAINT company_company_name IF NOT EXISTS
        for (c:Company) REQUIRE c.company_name IS UNIQUE
        """
    )
    tx.run(
        """CREATE CONSTRAINT position_position_name IF NOT EXISTS
        for (p:Position) REQUIRE p.position_name IS UNIQUE
        """
    )


def merge_data(tx):
    """Merge data to the ontology.

    Args:
        tx (Transaction): The Neo4j transaction object.
        response_text (str): The response text containing RDF/XML data.

    Returns:
        None
    """
    tx.run(
        """
        MATCH (n:News)-[:ONTOLOGY]->(ns1:ns1__DocInfo)-[*..1]-(ns3:ns3__SocialTag)
        MERGE (t:Tag {tag_name: ns3.ns0__name})
        MERGE (n)<-[:TAG_OF]-(t)
        """
    )
    tx.run(
        """
        MATCH (n:News)-[:ONTOLOGY]->(ns1:ns1__DocInfo)-[*..2]-(ns5:ns5__Person)
        MERGE (p:Person {person_name: ns5.ns0__name})
        MERGE (n)<-[:PERSON_OF]-(p)
        """
    )
    tx.run(
        """
        MATCH (n:News)-[:ONTOLOGY]->(ns1:ns1__DocInfo)-[*..2]-(ns5:ns5__Organization)
        MERGE (o:Organisation {organisation_name: ns5.ns0__name})
        MERGE (n)<-[:ORGANISATION__OF]-(o)
        """
    )
    tx.run(
        """
        MATCH (n:News)-[:ONTOLOGY]->(ns1:ns1__DocInfo)-[*..1]-(ns3:ns3__Industry)
        MERGE (i:Industry {industry_name: ns3.ns0__name})
        MERGE (n)<-[:INDUSTRY_OF]-(i)
        """
    )
    tx.run(
        """
        MATCH (n:News)-[:ONTOLOGY]->(ns1:ns1__DocInfo)-[*..2]-(ns5:ns5__Company)
        MERGE (c:Company {company_name: ns5.ns0__name})
        MERGE (n)<-[:COMPANY_OF]-(c)
        """
    )
    tx.run(
        """
        MATCH (n:News)-[:ONTOLOGY]->(ns1:ns1__DocInfo)-[*..2]-(ns5:ns5__Position)
        MERGE (p:Position {position_name: ns5.ns0__name})
        MERGE (n)<-[:POSITION_OF]-(p)
        """
    )


# Create the driver instance and merge the data
driver = None
try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    driver.verify_connectivity()
    with driver.session() as session:
        results = session.execute_write(create_constraints)
    with driver.session() as session:
        results = session.execute_write(merge_data)

except Exception as e:
    logging.error(f"Failed to create Neo4j driver: {e}")

# Close the driver instance
driver.close()
