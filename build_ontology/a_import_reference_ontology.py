"""
This module is used to interact with a Neo4j database. It includes
functionality to:

1. Create a configuration for the Neo4j database using the
`create_config` function.
2. Create a unique URI constraint for resources in the Neo4j database
using the `create_constraint` function.
3. Load a reference ontology into the Neo4j database using the
`load_reference_ontology` function.

The module uses the `neo4j` package to create a driver instance for
connecting to the Neo4j database. The connection details are fetched
from a `secrets.toml` file.

The module also uses the `logging` package to log any unexpected errors
that occur during the execution of the code.

Note: The `load_reference_ontology` function is currently not working
as expected and the ontology has to be manually imported in the Neo4j browser.
"""

import logging
import streamlit as st
from neo4j import GraphDatabase

# Set variables for Neo4j driver
SECRETS = "secrets.toml"
uri = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]


def create_config(tx):
    """
    Create config.
    """
    tx.run(
        """
        CALL n10s.graphconfig.init();
        """
    )


def create_constraint(tx):
    """
    Create uri constraint if it does not exist.
    """
    tx.run(
        """
        CREATE CONSTRAINT n10s_unique_uri IF NOT EXISTS FOR (r:Resource)
        REQUIRE r.uri IS UNIQUE;
        """
    )


# !! to do - this is not working, having to manually import the ontology
# in the Neo4j browser
def load_reference_ontology(tx):
    """
    Load the reference ontology.
    """
    tx.run(
        """
        CALL n10s.onto.import.fetch("file:///C:\\Users\\mikej\\Documents\\GitHub\\tikos-rns-demo\\build_ontology\\onecalais.owl.allmetadata.xml", "RDF/XML");
        """
    )


# Create the driver instance
DRIVER = None
try:
    DRIVER = GraphDatabase.driver(uri, auth=(username, password))
    DRIVER.verify_connectivity()
    with DRIVER.session() as session:
        session.execute_write(create_config)
        print("Config created")

except Exception as e:
    logging.error("An unexpected error occurred: %s", e)

# Close the driver instance
DRIVER.close()


# Create the driver instance
DRIVER = None
try:
    DRIVER = GraphDatabase.driver(uri, auth=(username, password))
    DRIVER.verify_connectivity()
    with DRIVER.session() as session:
        session.execute_write(create_constraint)
        print("Constraint created")

except Exception as e:
    logging.error("An unexpected error occurred: %s", e)

# Close the driver instance
DRIVER.close()


# Create the driver instance
DRIVER = None
try:
    DRIVER = GraphDatabase.driver(uri, auth=(username, password))
    DRIVER.verify_connectivity()
    with DRIVER.session() as session:
        session.execute_write(load_reference_ontology)
        print("Reference ontology loaded")

except Exception as e:
    logging.error("An unexpected error occurred: %s", e)

# Close the driver instance
DRIVER.close()
