import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import tool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools import ArxivQueryRun
from langchain import hub
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

openai_api_key = os.environ["OPENAI_API_KEY"]

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")


@tool("GoogleSearch")
def search(query_string: str):
    """
    Useful to search for any kinds of information and
    when you need to search the internet for any kinds of information, use this tool.
    Prefer this tool when you search for long queries.
    Should not be used for Article search or Topic Search.
    You should use this only when you need to get real-time information about a topic.
    """

    search = GoogleSerperAPIWrapper()

    return search.run(query_string)


api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
wiki = WikipediaQueryRun(
    name="WikiepdiaSearch",
    description="Use this tool when you want to analyze for information on Wikipedia by Terms, Keywords or any Topics.",
    api_wrapper=api_wrapper)

loader = WebBaseLoader("https://docs.smith.langchain.com")
docs = loader.load()
documents = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
).split_documents(docs)

vectordatabase = FAISS.from_documents(documents, OpenAIEmbeddings())
retriever = vectordatabase.as_retriever()
retriever_tool = create_retriever_tool(
    retriever,
    "langsmith_search",
    "search for information about langsmith. for any questions related to langsmith, you must use this tool"
)

arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)
tools = [arxiv, search, wiki, retriever_tool]

llm = ChatOpenAI(
    model="gpt-4o",
    max_tokens=2000,
    temperature=0.1,
    openai_api_key=openai_api_key
)

prompt = hub.pull("hwchase17/openai-functions-agent")

agent_executor = create_react_agent(
    llm,
    tools=tools
)
