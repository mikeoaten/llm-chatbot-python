# tag::import[]
from langchain.chains import GraphCypherQAChain

from llm import llm
from graph import graph

from langchain.prompts.prompt import PromptTemplate

# end::import[]

# tag::prompt[]
CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about company news.
Convert the user's question based on the schema.

Do not use any other node lables, relationship types, or properties that are not provided.

Example Cypher Statements:

1. Which companies have published news?:
```
MATCH (c:Company)<-[:PUBLISHED_BY]-(n:News WHERE n.headline_name_embedding IS NOT NULL)
RETURN c.name
```

Schema:
{schema}

Question:
{question}
"""
# end::prompt[]

# tag::template[]
cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)
# end::template[]

# tag::cypher-qa[]
cypher_qa = GraphCypherQAChain.from_llm(
    llm, graph=graph, verbose=True, cypher_prompt=cypher_prompt
)
# tag::cypher-qa[]


# tag::generate-response[]
def generate_response(prompt):
    """
    Use the Neo4j recommendations dataset to provide
    context to the LLM when answering a question
    """

    # Handle the response
    response = cypher_qa.run(prompt)

    return response


# end::generate-response[]
