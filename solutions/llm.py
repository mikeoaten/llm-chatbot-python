# tag::llm[]
import streamlit as st
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    openai_api_key=st.secrets["OPENAI_API_KEY"],
    model=st.secrets["OPENAI_MODEL"]
)
# end::llm[]

# tag::embedding[]
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    openai_api_key=st.secrets["OPENAI_API_KEY"],
    model = "text-embedding-ada-002",
    show_progress_bar = True
)
# end::embedding[]
