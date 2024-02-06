"""
This module provides functionality to interact with a Neo4j database.
It includes functions to delete all nodes and relationships, and to
drop all constraints and indexes (except defaul indexes) from the database. 

The module uses the neo4j and streamlit libraries to establish a connection
with the database using credentials stored in a secrets.toml file. The user
is prompted to confirm whether they want to delete all nodes and relationships.
If confirmed, the module executes the deletion and then proceeds to drop all
constraints and indexes.

In case of any exceptions during the execution, such as service unavailability
or authentication errors, the module logs the error and closes the database
connection.
"""

import logging
from neo4j import GraphDatabase
import streamlit as st


# Set variables for Neo4j driver
SECRETS = "secrets.toml"
uri = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]


def delete_all_nodes_and_relationships(tx):
    """
    Delete all nodes and relationships in the Neo4j database.
    """
    tx.run("MATCH (n) DETACH DELETE n")


def drop_all_constraints_and_indexes(tx):
    """
    Drop all constraints and indexes in the Neo4j database.
    """
    # Get all constraints
    constraints = tx.run("SHOW CONSTRAINTS").data()
    # Drop each constraint
    for constraint in constraints:
        tx.run(f"DROP CONSTRAINT {constraint['name']}")

    # Get all indexes
    indexes = tx.run("SHOW INDEXES").data()
    # Drop each index, except for indexes of type "LOOKUP"
    for index in indexes:
        if index["type"] != "LOOKUP":
            tx.run(f"DROP INDEX {index['name']}")


# Ask the user whether to delete all nodes and relationships
delete_data = input("Delete all nodes and relationships? (yes/no) ") == "yes"

# Import the drop_all_constraints_and_indexes function
# Create the driver instance
DRIVER = None
try:
    DRIVER = GraphDatabase.driver(uri, auth=(username, password))
    with DRIVER.session() as session:
        if delete_data:
            # Delete all nodes and relationships in a separate transaction
            session.execute_write(delete_all_nodes_and_relationships)
            print("All nodes and relationships deleted.")
        # Call the drop_all_constraints_and_indexes function
        session.execute_write(drop_all_constraints_and_indexes)
        print("All constraints and indexes dropped.")

except Exception as e:
    logging.error("An unexpected error occurred: %s", e)

finally:
    if DRIVER is not None:
        DRIVER.close()
