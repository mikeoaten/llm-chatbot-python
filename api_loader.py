import requests
import json
from neo4j import GraphDatabase
import streamlit as st
import logging


# Set variables for Neo4j driver
secrets = ('secrets.toml')
uri=st.secrets["NEO4J_URI"]
username=st.secrets["NEO4J_USERNAME"]
password=st.secrets["NEO4J_PASSWORD"]

# Set variable for newsid list
newsid = [15945972, 15946476, 16205855, 16217157, 16232531, 16249216]
    

def create_constraint(tx):
    """
    Create a constraint on the 'Rns' label and 'id' property if it doesn't already exist.
    """
    tx.run("CREATE CONSTRAINT rns_id IF NOT EXISTS FOR (n:Rns) REQUIRE n.id IS UNIQUE")


def merge_data(tx, id, newsarticle):
    """
    Merge data into Neo4j graph database.

    Parameters:
    - tx: Neo4j transaction object
    - id: News ID
    - newsarticle: News article data in JSON format
    """
    tx.run("MERGE (n:Rns {id: $id, newsarticle: $newsarticle})", id=id, newsarticle=newsarticle)


# Create the driver instance
driver = None
try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        # Create constraint if it doesn't exists
        session.execute_write(create_constraint)
        # Loop through API called with newsids
        for id in newsid:
            response = requests.get(f'https://api.londonstockexchange.com/api/v1/pages?path=news-article&parameters=newsId%253D{id}')
            # Decode the _content field from bytes to a string
            data = response.__dict__['_content'].decode("utf-8")
            # Load as json
            rnss = json.loads(data)

            # Isolate the 'newsarticle' data
            for component in rnss['components']:
                for content in component['content']:
                    if content['name'] == 'newsarticle':
                        # Format 'newsarticle' as JSON
                        newsarticle = json.dumps(content['value'], indent=1)
                        # Create constraint if it doesn't exists
                        session.execute_write(merge_data, id, newsarticle)
except Exception as e:
    logging.error(f"Failed to create Neo4j driver: {e}")
                

# Close the driver instance
driver.close()