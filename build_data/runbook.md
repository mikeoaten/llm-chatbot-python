# delete_data_drop_neo4_constraints_indexes.py
Clear out Neo4j db prior to loading, this will require a yes/no in the terminal to
delete data as well as indexes/constraints

# extract_links
Save the html page generated from the search function at https://www.londonstockexchange.com/news?tab=news-explorer
In auxilaries
name it news_download.html


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


# changes to installed pacckages
# text_splitter.py ln 89-91
# If there is only one sentence, return it as a single chunk
if len(single_sentences_list) == 1:
    return [text]