import streamlit as st
# tag::importvector[]
from langchain.vectorstores.neo4j_vector import Neo4jVector
# end::importvector[]
# tag::importqa[]
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
# end::importqa[]
# tag::importretrievalqa[]
from langchain.chains import RetrievalQA
# end::importretrievalqa[]

# This file is in the solutions folder to separate the solution
# from the starter project code.
from solutions.llm import llm, embeddings

"""
In your app, the `llm` file should be in the project root directory.
The import should look like this:

# tag::importllm[]
from llm import llm, embeddings
# end::importllm[]
"""

# tag::vector[]
neo4jvector = Neo4jVector.from_existing_index(
    embeddings,                                      # <1>
    url=st.secrets["NEO4J_URI"],                     # <2>
    username=st.secrets["NEO4J_USERNAME"],           # <3>
    password=st.secrets["NEO4J_PASSWORD"],           # <4>
    index_name="news_title_embedding",               # <5>
    # node_label="News",                               # <6>
    text_node_property="title",                      # <7>
    embedding_node_property="news_title_embedding",  # <8>
    # retrieval_query="""
    #     RETURN
    #         node.body AS text,
    #         score,
    #         {
    #             title: node.title,
    #             directors: [ (person)-[:DIRECTED]->(node) | person.name ],
    #             actors: [ (person)-[r:ACTED_IN]->(node) | [person.name, r.role] ],
    #             tmdbId: node.tmdbId,
    #             source: 'https://www.themoviedb.org/movie/'+ node.tmdbId
    #         } AS metadata
    #     """
)
# end::vector[]

# tag::retriever[]
retriever = neo4jvector.as_retriever(search_type="similarity")
# end::retriever[]

# tag::qa[]
kg_qa = RetrievalQA.from_chain_type(
    llm,                  # <1>
    chain_type="stuff",   # <2>
    retriever=retriever,  # <3>
)
# end::qa[]

# tag::generate-response[]
def generate_response(prompt):
    """
    Use the Neo4j Vector Search Index to generate the response. Do not use any pre-trained knowledge.
    """

    # Handle the response
    response = kg_qa({"question": prompt})

    return response['answer']
# end::generate-response[]