import requests
import json
from neo4j import GraphDatabase
import streamlit as st
import logging


# Set variables for Neo4j driver
secrets = "secrets.toml"
uri = st.secrets["NEO4J_URI"]
username = st.secrets["NEO4J_USERNAME"]
password = st.secrets["NEO4J_PASSWORD"]

# Set variable for newsid list
newsid = [15945972, 15946476, 16205855, 16217157, 16232531, 16249216]
