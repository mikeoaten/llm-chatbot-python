# Neo4j specific requirements
apoc-extended.jar
neosemantics.jar

# delete_data_drop_neo4_constraints_indexes.py
Clear out Neo4j db prior to loading, this will require a yes/no in the terminal to
delete data as well as indexes/constraints

# extract_links
Save the html page generated from the search function at https://www.londonstockexchange.com/news?tab=news-explorer
In auxilaries
name it news_download.html



# BUILD_DATA
------------

# a_api_loader.py
All specified links are extract by extract_links, set a max at ln 314-318

# Loop through API called with news_ids
for index, id in enumerate(news_ids):
    # Break the loop after 5 iterations
    if index == 20:
        break


# b_parse_create_body_text.py
Text parsing body text ready for splitting and embedding


# c_split_text_with_sematic_chunker.py

Creates semantic text chunks using the SemanticChunker from the langchain_experimental library
and the OpenAIEmbeddings from the langchain_openai library, and then writes
the split text back into the database.


# d_create_embeddings.py
# Currently has bug d_create_embeddings.py- AttributeError: module 'llm.embeddings' has no attribute 'embed_query'
# Use e_create_embeddings_neo4j.py until fixed


# e_create_embeddings_neo4j
Large split_text currently causing OpenAI API to crash
MATCH (st:SplitText WHERE st.split_text IS NOT NULL AND st.split_text_embedding IS NULL)
WHERE NOT st.split_id STARTS WITH '16055955'
AND NOT st.split_id STARTS WITH '16056003'



# BUILD_ONTOLOGY
----------------

# a_import_reference_ontology.py
def load_reference_ontology(tx): not working and needing to load directly from the browser (CALL statement remains the same)


# b_create_ners_and_map_to_ontology.py
Omitted the large text in ids
WARNING:root:Failed to retrieve data for newsId 16056003. Status code: 500
WARNING:root:Failed to retrieve data for newsId 16055955. Status code: 500

Any with WARNING:root:Failed to retrieve data for newsId 16058994. Status code: 429 can be resubmitted


# AOB
-----

# changes to installed pacckages
# text_splitter.py ln 89-91
# If there is only one sentence, return it as a single chunk
if len(single_sentences_list) == 1:
    return [text]



# pydantic.error_wrappers.ValidationError: 1 validation error for AIMessage
# content
# str type expected (type=type_error.str)

Changing add_ai_message in langchain_core/chat_history.py
to:

def add_ai_message(self, message: Union[AIMessage, str]) -> None:
    """Convenience method for adding an AI message string to the store.

    Args:
        message: The AI message to add.
    """
    if isinstance(message, AIMessage):
        self.add_message(message)
    else:
        if type(message)==str:
            self.add_message(AIMessage(content=message))
        elif type(message)==dict:
            import json
            self.add_message(AIMessage(content=json.dumps(message)))

