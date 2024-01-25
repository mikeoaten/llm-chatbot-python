import streamlit as st
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from llm import llm, embeddings
from langchain.chains import RetrievalQA

# for news_body_embedding index
# retrieval_query = """
# RETURN
#     node.body AS text,
#     score,
#     node {
#         score: score,
#         headline_name: node.headline_name,
#         url: node.url,
#         company: [(node)-[:PUBLISHED_BY]->(Company) | Company.company_name]
#     } AS metadata
# """

# for split_text_embedding index
retrieval_query = """
MATCH (node)-[:CHILD_OF]->(n:News)-[:PUBLISHED_BY]->(c:Company)
MATCH path = (node)-[r*..2]-()
RETURN
n.body AS text, // this is returning the parent text after matching on the child text
path,
score,
node {
    score: score,
    split_id: node.split_id,
    // split_source: node.split_source,
    company: [(node)-[:CHILD_OF]->(n:News)-[:PUBLISHED_BY]->(Company) | Company.company_name],
    url: [(node)-[:CHILD_OF]->(n:News) | n.url],
        graph: [node in nodes(path) | {
        node_id: ID(node),
        labels: labels(node),
        relationships: [rel in relationships(path) | {
            rel_id: ID(rel),
            rel_type: type(rel),
            start_node_id: ID(startNode(rel)),
            end_node_id: ID(endNode(rel))
        }]
    }]
} AS metadata
"""


# neo4jvector = Neo4jVector.from_existing_index(
#     embeddings,
#     url=st.secrets["NEO4J_URI"],
#     username=st.secrets["NEO4J_USERNAME"],
#     password=st.secrets["NEO4J_PASSWORD"],
#     index_name="news_body_embedding",
#     retrieval_query=retrieval_query,
#     # text_node_property="body",
#     # database="neo4j",
#     # node_label="News",
#     # embedding_node_property="body_embedding",
# )

neo4jvector = Neo4jVector.from_existing_index(
    embeddings,
    url=st.secrets["NEO4J_URI"],
    username=st.secrets["NEO4J_USERNAME"],
    password=st.secrets["NEO4J_PASSWORD"],
    index_name="split_text_embedding",
    retrieval_query=retrieval_query,
    # text_node_property="body",
    # database="neo4j",
    # node_label="SplitText",
    # embedding_node_property="body_embedding",
)

retriever = neo4jvector.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 3, "score_threshold": 0.87},
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
