"""Document retriever tool for LangSmith documentation."""

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import create_retriever_tool as create_langchain_retriever_tool
from config.settings import settings


def create_retriever_tool():
    """
    Create and return the document retriever tool for LangSmith documentation.
    
    This tool loads documents from the LangSmith documentation website,
    splits them into chunks, creates a vector database, and returns a retriever tool.
    
    Returns:
        Retriever tool for searching LangSmith documentation
    """
    # Load documents from LangSmith documentation
    loader = WebBaseLoader(settings.LANGSMITH_DOCS_URL)
    docs = loader.load()
    
    # Split documents into chunks
    documents = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    ).split_documents(docs)
    
    # Create vector database
    vectordatabase = FAISS.from_documents(documents, OpenAIEmbeddings())
    retriever = vectordatabase.as_retriever()
    
    # Create retriever tool
    retriever_tool = create_langchain_retriever_tool(
        retriever,
        "langsmith_search",
        "search for information about langsmith. for any questions related to langsmith, you must use this tool"
    )
    
    return retriever_tool
