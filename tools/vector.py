import streamlit as st
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from llm import llm, embeddings
from langchain.chains import RetrievalQA


retrieval_query = """
RETURN
    node.body AS text,
    score,
    node {
        headline_name: node.headline_name,
        source: node.id,
        sector: node.sector,
        rns_number: node.rnsnumber,
        company: [(node)-[:PUBLISHED_BY]->(Company) | Company.company_name]
    } AS metadata
"""


neo4jvector = Neo4jVector.from_existing_index(
    embeddings,
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"],
    index_name="news_body_embedding",
    retrieval_query=retrieval_query,
    # text_node_property="body",
    # database="neo4j",
    # node_label="News",
    # embedding_node_property="body_embedding",
)

retriever = neo4jvector.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3},
)


kg_qa = RetrievalQA.from_chain_type(
    llm,
    chain_type="stuff",
    retriever=retriever,
)


def generate_response(prompt):
    """
    Use the Neo4j Vector Search Index
    to augment the response from the LLM
    """

    # Handle the response
    response = kg_qa({"question": prompt})
    return response["answer"]
