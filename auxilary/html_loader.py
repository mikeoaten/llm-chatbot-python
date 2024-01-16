# for testing html scraper, does not access meta data so will use api calls instead
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer

# Load HTML
loader = AsyncChromiumLoader(["https://python.langchain.com/docs/use_cases/web_scraping"])
html = loader.load()

# Transform
bs_transformer = BeautifulSoupTransformer()
docs_transformed = bs_transformer.transform_documents(html, tags_to_extract=["body"])

# Result
print(docs_transformed[0].page_content[0:500])