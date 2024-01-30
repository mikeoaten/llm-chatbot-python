# https://neo4j.com/labs/neosemantics/4.3/config/
# Import RDF data

# The method n10s.graphconfig.init can help us with this setup.
# Calling the procedure without parameters will set all the default values:
# CALL n10s.graphconfig.init();

# The Graph Configuration can be removed by invoking and then
# reloading/refreshing the browser
# CALL n10s.graphconfig.drop

# Current set up listed with
# CALL n10s.graphconfig.show

# List namespaces
# CALL n10s.nsprefixes.list

import logging
import streamlit as st
from neo4j import GraphDatabase

# Set variables for Neo4j driver
secrets = "secrets.toml"
uri = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]


def create_uri_constraint(tx):
    """
    Create uri constraint if it does not exist.
    """
    tx.run(
        """
        CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource)
        REQUIRE r.uri IS UNIQUE;
        """
    )


def load_reference_ontology(tx):
    """
    Load the reference ontology.
    """
    tx.run(
        """
        CALL n10s.onto.import.fetch("file:///C:\\Users\\mikej\\Documents\\GitHub\\llm-chatbot-python\\build_ontology\\onecalais.owl.allmetadata.xml", "RDF/XML");
        """
    )


# Create the driver instance
driver = None
try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    driver.verify_connectivity()
    with driver.session() as session:
        session.execute_write(create_uri_constraint)
    with driver.session() as session:
        session.execute_write(load_reference_ontology)

except Exception as e:
    logging.error(f"Failed to create Neo4j driver: {e}")

# Close the driver instance
driver.close()
