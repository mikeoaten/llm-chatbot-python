import streamlit as st
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from llm import llm, embeddings

# from langchain.chains.qa_with_sources import load_qa_with_sources_chain

from langchain.chains import RetrievalQA

# This file is in the solutions folder to separate the solution
# from the starter project code.


neo4jvector = Neo4jVector.from_existing_index(
    embeddings,
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"],
    index_name="news_headline_embedding",
    database="neo4j",
    node_label="News",
    text_node_property="headline_name",
    embedding_node_property="headline_name_embedding",
    retrieval_query="""
RETURN
    node.title AS text,
    score,
    {
        headline_name: node.headline_name,
        source: node.id,
        sector: node.sector,
        id: id(node),
        rns_number: node.rnsnumber,
        company: [ (node)-[:PUBLISHED_BY]->(Company) | Company.company_name]
    } AS metadata
""",
)

retriever = neo4jvector.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 10, "score_threshold": 0.0},
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
