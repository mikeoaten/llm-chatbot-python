"""
This module is used to fetch news articles from the London Stock
Exchange API and store them in a Neo4j graph database.

The module uses the requests library to make HTTP requests to the API,
and the neo4j library to interact with the Neo4j database. It also uses
the json library to parse the API responses, and the streamlit library
to manage secrets.

The module defines several functions to interact with the Neo4j database:
- create_constraints: Creates constraints in the database if they do not exist.
- merge_newsarticle_nodes: Merges news article nodes into the database.
- merge_newsarticle_relationships: Merges relationships between nodes in the database.

The module also includes a main script that:
- Establishes a connection to the Neo4j database.
- Loops through a list of news article IDs, fetches the corresponding articles
from the API, and stores them in the database.
- Logs any errors that occur during this process.

The module assumes that the following secrets are defined:
- NEO4J_URI: The URI of the Neo4j database.
- NEO4J_USERNAME: The username to use when connecting to the Neo4j database.
- NEO4J_PASSWORD: The password to use when connecting to the Neo4j database.
"""

import json
import logging
import requests
import streamlit as st

from neo4j import GraphDatabase
from z_extract_links import news_ids


# Set variables for Neo4j driver
SECRETS = "secrets.toml"
uri = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]


def create_constraints(tx):
    """
    Create constraints if they do not exist.
    """
    tx.run(
        """
        CREATE CONSTRAINT rns_id IF NOT EXISTS
        FOR (r:Rns) REQUIRE r.id IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT company_companyname IF NOT EXISTS
        FOR (c:Company) REQUIRE c.companyname IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT date_date IF NOT EXISTS
        FOR (d:Date) REQUIRE d.date IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT news_id IF NOT EXISTS
        FOR (n:News) REQUIRE n.id IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT newscategory_category IF NOT EXISTS
        FOR (n:NewsCategory) REQUIRE n.category IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT industry_industry IF NOT EXISTS
        FOR (i:Industry) REQUIRE i.industry IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT sector_sector IF NOT EXISTS
        FOR (s:Sector) REQUIRE s.sector IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT subsector_subsector IF NOT EXISTS
        FOR (s:SubSector) REQUIRE s.subsector IS UNIQUE
        """
    )
    tx.run(
        """
        CREATE CONSTRAINT supersector_supersector IF NOT EXISTS
        FOR (s:SuperSector) REQUIRE s.supersector IS UNIQUE
        """
    )


def merge_newsarticle_nodes(
    tx,
    id,
    news_article,
    company_name,
    title,
    source,
    datetime,
    rns_number,
    category,
    headline_name,
    industry,
    supersector,
    sector,
    subsector,
    tidm,
):
    """
    Merge newsarticle nodes into Neo4j graph database.

    Parameters:
    - tx: Neo4j transaction object
    - id: ID
    - news_article: News article
    - company_name: Company name
    - title: News title
    - source: News source
    - datetime: Datetime
    - rns_number: RNS number
    - category: News category
    - headline_name: Headline name
    - industry: Industry
    - supersector: Supersector
    - sector: Sector
    - subsector: Subsector
    - tidm: TIDM
    """
    tx.run(
        "MERGE (:Rns {id: $id, news_article: $news_article})",
        id=id,
        news_article=news_article,
    )
    tx.run(
        """MERGE (:Company {
                            company_name: $company_name,
                            industry: $industry,
                            supersector: $supersector,
                            sector: $sector,
                            subsector: $subsector,
                            tidm: $tidm
                            }
                )
        """,
        company_name=company_name,
        industry=industry,
        supersector=supersector,
        sector=sector,
        subsector=subsector,
        tidm=tidm,
    )
    tx.run(
        """
        MERGE (:News
                    {id: $id,
                    title: $title,
                    source: $source,
                    datetime: $datetime,
                    company_name: $company_name,
                    rns_number: $rns_number,
                    category: $category,
                    headline_name: $headline_name,
                    tidm: $tidm,
                    industry: $industry,
                    supersector: $supersector,
                    sector: $sector,
                    subsector: $subsector
                    }
                )
        """,
        id=id,
        title=title,
        source=source,
        datetime=datetime,
        company_name=company_name,
        rns_number=rns_number,
        category=category,
        headline_name=headline_name,
        tidm=tidm,
        industry=industry,
        supersector=supersector,
        sector=sector,
        subsector=subsector,
    )
    tx.run(
        "MERGE (:NewsCategory {category: $category})",
        category=category,
    )
    tx.run(
        "MERGE (:Date {date: left($datetime, 10)})",
        datetime=datetime,
    )
    tx.run(
        "MERGE (:Industry {industry: $industry})",
        industry=industry,
    )
    tx.run(
        "MERGE (:SuperSector {supersector: $supersector})",
        supersector=supersector,
    )
    tx.run(
        "MERGE (:Sector {sector: $sector})",
        sector=sector,
    )
    tx.run(
        "MERGE (:SubSector {subsector: $subsector})",
        subsector=subsector,
    )


def merge_newsarticle_relationships(
    tx,
):
    """
    Merge newsarticle relationships into Neo4j graph database.

    Parameters:
    - tx: Neo4j transaction object
    """
    tx.run(
        """
        MATCH
            (r:Rns),
            (n:News)
        WHERE r.id = n.id
        AND NOT EXISTS ((r)-[:SOURCE_OF]->(n))
        CREATE (r)-[:SOURCE_OF]->(n);
        """
    )
    tx.run(
        """
        MATCH
            (n:News),
            (d:Date)
        WHERE d.date = left(n.datetime, 10)
        CREATE (n)-[:PUBLISHED_ON]->(d);        
        """
    )
    tx.run(
        """
        MATCH
            (n:News),
            (nc:NewsCategory)
        WHERE n.category = nc.category
        CREATE (n)-[:CATEGORY]->(nc);
        """
    )
    tx.run(
        """
        MATCH
            (c:Company),
            (sbs:SubSector)
        WHERE c.subsector = sbs.subsector
        CREATE (c)-[:SUBSECTOR]->(sbs);
        """
    )
    tx.run(
        """
        MATCH
            (c:Company),
            (s:Sector)
        WHERE c.sector = s.sector
        CREATE (c)-[:SECTOR]->(s);
        """
    )
    tx.run(
        """
        MATCH
            (c:Company),
            (ss:SuperSector)
        WHERE c.supersector = ss.supersector
        CREATE (c)-[:SUPERSECTOR]->(ss);
        """
    )
    tx.run(
        """
        MATCH
            (c:Company),
            (i:Industry)
        WHERE c.industry = i.industry
        CREATE (c)-[:INDUSTRY]->(i);
        """
    )
    tx.run(
        """
        MATCH
            (c:Company),
            (n:News)
        WHERE c.company_name = n.company_name
        CREATE (n)-[:PUBLISHED_BY]->(c);
        """
    )


# Create the driver instance
DRIVER = None
try:
    DRIVER = GraphDatabase.driver(uri, auth=(username, password))
    DRIVER.verify_connectivity()
    with DRIVER.session() as session:
        # Create constraint if it doesn't exists
        session.execute_write(create_constraints)
        print("Constraints created")

        # Loop through API called with news_ids
        for index, id in enumerate(news_ids):
            # Break the loop after 5 iterations
            if index == 100:
                break
            response = requests.get(
                f"https://api.londonstockexchange.com/api/v1/pages?path=news-article&parameters=newsId%253D{id}",
                timeout=5,
            )
            # Decode the _content field from bytes to a string
            data = response.__dict__["_content"].decode("utf-8")
            # Load as json
            rnss = json.loads(data)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # ETL 'specific' data
                for component in rnss["components"]:
                    for content in component["content"]:
                        if content["name"] == "newsarticle":
                            # Format data
                            id = content["value"]["id"]
                            news_article = json.dumps(content["value"], indent=1)
                            company_name = content["value"]["companyname"]
                            title = content["value"]["title"]
                            source = content["value"]["source"]
                            datetime = content["value"]["datetime"]
                            rns_number = content["value"]["rnsnumber"]
                            category = content["value"]["category"]
                            headline_name = content["value"]["headlinename"]

                        if content["name"] == "issuerreferencedata":
                            # Format data
                            industry = content["value"]["icbindustry"]
                            supersector = content["value"]["icbsupersector"]
                            sector = content["value"]["icbsector"]
                            subsector = content["value"]["icbsubsector"]

                        if content["name"] == "pricedata":
                            # Format data
                            tidm = content["value"]["tidm"]

                # Merge nodes
                session.execute_write(
                    merge_newsarticle_nodes,
                    id,
                    news_article,
                    company_name,
                    title,
                    source,
                    datetime,
                    rns_number,
                    category,
                    headline_name,
                    industry,
                    supersector,
                    sector,
                    subsector,
                    tidm,
                )
                print("Nodes merged")
            else:
                logging.warning(
                    f"Failed to retrieve data for newsId {id}. Status code: {response.status_code}"
                )

        # Merge relationships
        session.execute_write(merge_newsarticle_relationships)
        print("Relationships merged")

except Exception as e:
    logging.error("An unexpected error occurred: %s", e)


# Close the driver instance
DRIVER.close()
print("driver closed")
