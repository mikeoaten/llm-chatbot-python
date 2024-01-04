import streamlit as st
from solutions.llm import llm, embeddings
from langchain.vectorstores.neo4j_vector import Neo4jVector

# embedding_provider = OpenAIEmbeddings(openai_api_key="sk-...")

test_vector = Neo4jVector.from_existing_index(
    embeddings,                                      # <1>
    url=st.secrets["NEO4J_URI"],                     # <2>
    username=st.secrets["NEO4J_USERNAME"],           # <3>
    password=st.secrets["NEO4J_PASSWORD"],           # <4>
    index_name="news_title_embedding",               # <5>
    node_label="News",                               # <6>
    text_node_property="title",                      # <7>
    embedding_node_property="news_title_embedding"   # <8>
)

r = test_vector.similarity_search_with_relevance_scores(
    "News titles which are like 'Publication of Suppl.Prospects' ",
    k=10)

for doc, score in r:
    print("-" * 80)
    print("Score: ", score)
    print(doc.page_content)