from neo4j import GraphDatabase
import streamlit as st
import logging

# Set variables for Neo4j driver
secrets = ('secrets.toml')
uri=st.secrets["NEO4J_URI"]
username=st.secrets["NEO4J_USERNAME"]
password=st.secrets["NEO4J_PASSWORD"]

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
        if index['type'] != 'LOOKUP':
            tx.run(f"DROP INDEX {index['name']}")

# Ask the user whether to delete all nodes and relationships
delete_data = input("Delete all nodes and relationships? (yes/no) ") == "yes"

# Import the drop_all_constraints_and_indexes function
# Create the driver instance
driver = None
try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        if delete_data:
            # Delete all nodes and relationships in a separate transaction
            session.execute_write(delete_all_nodes_and_relationships)
        # Call the drop_all_constraints_and_indexes function
        session.execute_write(drop_all_constraints_and_indexes)

except Exception as e:
    logging.error(f"Failed to create Neo4j driver: {e}")
finally:
    if driver is not None:
        driver.close()