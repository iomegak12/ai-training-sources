"""
SQL Query Tool for Chinook Database (Music Store)
Uses the Complex Answer Chain pattern to handle natural language queries
"""
from operator import itemgetter
from typing import Optional
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

# Lazy-loaded global instances
_db: Optional[SQLDatabase] = None
_llm: Optional[ChatOpenAI] = None
_sql_chain = None


def get_database() -> SQLDatabase:
    """
    Get or create the Chinook database connection
    
    Returns:
        SQLDatabase instance for Chinook
    """
    global _db
    
    if _db is None:
        db_path = settings.chinook_database_full_path
        db_uri = f"sqlite:///{db_path}"
        _db = SQLDatabase.from_uri(db_uri)
        logger.info(f"Chinook database connection initialized: {db_path}")
    
    return _db


def get_llm() -> ChatOpenAI:
    """
    Get or create the LLM instance for SQL query generation
    
    Returns:
        ChatOpenAI instance
    """
    global _llm
    
    if _llm is None:
        _llm = ChatOpenAI(
            model=settings.sql_model_name,
            temperature=settings.sql_temperature,
            max_tokens=settings.sql_max_tokens,
            openai_api_key=settings.openai_api_key
        )
        logger.info(f"SQL LLM initialized: {settings.sql_model_name}")
    
    return _llm


def parse_sql_query(query_string: str) -> str:
    """
    Parse the SQL query string to extract the actual query.
    Handles cases where LLM returns formatted output with prefixes.
    
    Args:
        query_string: Raw query string from LLM
        
    Returns:
        Cleaned SQL query string
    """
    # Remove common prefixes like "SQLQuery:", "--QUERY--:", etc.
    splitted_string = query_string.split(":")
    
    if len(splitted_string) >= 2:
        query = splitted_string[1].strip()
    else:
        query = query_string
    
    return query.strip()


def create_chinook_query_chain():
    """
    Create the Complex Answer Chain for Chinook database queries.
    
    Pattern: Question → SQL Generation → Execution → Professional Answer
    
    Returns a chain that:
    1. Takes a natural language question
    2. Generates appropriate SQL query
    3. Executes it against Chinook DB
    4. Returns a business-professional formatted answer
    
    Returns:
        Runnable chain for complex SQL query answering
    """
    global _sql_chain
    
    if _sql_chain is not None:
        return _sql_chain
    
    db = get_database()
    llm = get_llm()
    
    # Create SQL query writer
    write_query = create_sql_query_chain(llm=llm, db=db)
    
    # Create SQL executor
    execute_query = QuerySQLDataBaseTool(db=db)
    
    # Create answer prompt
    answer_prompt = PromptTemplate.from_template(
        """You are a helpful assistant analyzing a music store database (Chinook).
        
Given the following user question, corresponding SQL Query, and SQL Result, 
provide a clear, concise answer in business-professional English with specific 
details and explanations from the SQL Result.

If the result is empty or null, explain that no data was found.
If there are multiple results, summarize the key findings.

User Question: {question}
SQL Query: {query}
SQL Result: {result}

Answer: """
    )
    
    # Build the complex chain
    # Step 1: Pass question through
    # Step 2: Assign generated SQL to 'query' key
    # Step 3: Execute SQL and assign result to 'result' key
    # Step 4: Format into prompt and get LLM answer
    _sql_chain = (
        RunnablePassthrough.assign(query=write_query)
        .assign(
            result=itemgetter("query") 
            | RunnableLambda(parse_sql_query) 
            | execute_query
        )
        | answer_prompt 
        | llm 
        | StrOutputParser()
    )
    
    logger.info("✓ Chinook SQL query chain initialized")
    return _sql_chain


@tool("query_music_database")
def query_music_database_tool(question: str) -> str:
    """
    Query the Chinook music store database using natural language.
    
    Use this tool when the user asks analytical or complex questions about:
    - Music tracks, albums, artists, or genres
    - Customer purchases, invoices, or spending patterns
    - Employee information
    - Sales data, revenue, or financial analysis
    - Playlists and media types
    - Any question requiring JOIN operations, aggregations, or complex SQL
    
    This tool automatically:
    1. Converts your natural language question to SQL
    2. Executes the query against the music database
    3. Returns a professional, well-formatted answer with insights
    
    Database Schema includes:
    - Artist, Album, Track (music catalog)
    - Customer, Employee (people)
    - Invoice, InvoiceLine (sales transactions)
    - Genre, MediaType (categorization)
    - Playlist, PlaylistTrack (collections)
    
    Examples of good questions:
    - "Which artist has the most albums?"
    - "What are the top 5 bestselling tracks?"
    - "Which country's customers have spent the most?"
    - "How many tracks are in each genre?"
    - "What is the average invoice total by country?"
    
    Args:
        question: Natural language question about the music store data
        
    Returns:
        Professional answer with specific data and insights from the database
    """
    try:
        # Get or create the chain
        chain = create_chinook_query_chain()
        
        # Execute the chain
        result = chain.invoke({"question": question})
        
        return result
    
    except Exception as e:
        logger.error(f"Error querying music database: {str(e)}", exc_info=True)
        return f"Error querying music database: {str(e)}\n\nPlease try rephrasing your question or make it more specific."


def get_sql_tool():
    """
    Get the SQL query tool for Chinook database
    
    Returns:
        SQL query tool
    """
    logger.info("✓ SQL query tool (Chinook) initialized")
    return query_music_database_tool
