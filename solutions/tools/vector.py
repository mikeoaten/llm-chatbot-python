import streamlit as st

# tag::importvector[]
from langchain_community.vectorstores.neo4j_vector import Neo4jVector

# end::importvector[]
# tag::importqa[]
# from langchain.chains.qa_with_sources import load_qa_with_sources_chain
# end::importqa[]
# tag::importretrievalqa[]
from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQAWithSourcesChain

# end::importretrievalqa[]

# This file is in the solutions folder to separate the solution
# from the starter project code.
from solutions.llm import llm, embeddings

# tag::vector[]
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
# end::vector[]

# tag::retriever[]
retriever = neo4jvector.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 10, "score_threshold": 0.0},
)
# end::retriever[]

# tag::qa[]
kg_qa = RetrievalQA.from_chain_type(
    llm,  # <1>
    chain_type="stuff",  # <2>
    retriever=retriever,  # <3>
)
# end::qa[]

# kg_qa = RetrievalQAWithSourcesChain.from_chain_type(
#     llm,  # <1>
#     chain_type="stuff",  # <2>
#     retriever=retriever,  # <3>
# )


# tag::generate-response[]
def generate_response(prompt):
    """
    Use the Neo4j Vector Search Index to generate the response. Do not use any pre-trained knowledge.
    """

    # Handle the response
    response = kg_qa({"question": prompt})

    return response["answer"]


# end::generate-response[]

# docs = retriever.get_relevant_documents(query="News titles which are like 'Publication of Suppl.Prospects'", k=10)
