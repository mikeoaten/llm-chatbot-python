import streamlit as st
# tag::importvector[]
from langchain.vectorstores.neo4j_vector import Neo4jVector
# end::importvector[]
# tag::importqa[]
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
# end::importqa[]
# tag::importretrievalqa[]
from langchain.chains import RetrievalQA
# from langchain.chains import RetrievalQAWithSourcesChain
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
    database="neo4j",  # neo4j by default
    node_label="News",                               # <6>
    text_node_property="title",                      # <7>
    embedding_node_property="title_embedding",       # <8>
    retrieval_query="""
RETURN
    node.title AS text,
    score,
    {
        title: node.title,
        source: node.id,
        sector: node.sector,
        id: id(node),
        rns_number: node.rnsnumber,
        company: [ (node WHERE id(node) IN [2043, 2044, 2045, 2046, 11427, 11930])-[:PUBLISHED_BY]->(Company) | Company.issuername ]
    } AS metadata
""",
)
# end::vector[]

# tag::retriever[]
retriever = neo4jvector.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            'k': 10,
            'score_threshold': 0.0}
    )
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

# docs = retriever.get_relevant_documents(query="News titles which are like 'Publication of Suppl.Prospects'", k=10)