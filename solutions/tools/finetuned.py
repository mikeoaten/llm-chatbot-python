from langchain.chains import GraphCypherQAChain
# tag::import-prompt-template[]
from langchain.prompts.prompt import PromptTemplate
# end::import-prompt-template[]

from solutions.llm import llm
from solutions.graph import graph

# tag::prompt[]
CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about Company news from the RNS service of The London Stock Exchange.
Convert the user's question based on the schema.

Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.


Schema:
{schema}

Question:
{question}

Cypher Query:
"""
# end::prompt[]

# tag::template[]
cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)
# end::template[]


# tag::cypher-qa[]
cypher_qa = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=cypher_prompt
)
# tag::cypher-qa[]