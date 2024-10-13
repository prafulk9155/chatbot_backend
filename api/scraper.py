from bs4 import SoupStrainer 
from langchain_community.document_loaders import WebBaseLoader
# Adjust to target paragraph tags (common in Wikipedia for main content)
loader = WebBaseLoader(
    web_paths=["https://en.wikipedia.org/wiki/History_of_India"],
    bs_kwargs=dict(parse_only=SoupStrainer("p"))  # Target paragraph tags for main content
)