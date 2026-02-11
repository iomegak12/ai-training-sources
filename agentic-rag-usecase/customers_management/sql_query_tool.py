"""
SQL Query Tool for Chinook Database (Music Store)
Uses the Complex Answer Chain pattern to handle natural language queries
"""
import os
from operator import itemgetter
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_classic.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI


# Initialize database and LLM (lazy loaded)
_db = None
_llm = None
_sql_chain = None


def get_database():
    """Get or create the database connection"""
    global _db
    if _db is None:
        db_path = os.getenv("CHINOOK_DB_PATH", "sqlite:///db/chinook.db")
        _db = SQLDatabase.from_uri(db_path)
    return _db


def get_llm():
    """Get or create the LLM instance"""
    global _llm
    if _llm is None:
        model_name = "gpt-3.5-turbo"
        _llm = ChatOpenAI(
            model=model_name,
            temperature=0.1,
            max_tokens=2000,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    return _llm


def parse_sql_query(query_string: str) -> str:
    """
    Parse the SQL query string to extract the actual query.
    Handles cases where LLM returns formatted output with prefixes.
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
    """
    db = get_database()
    llm = get_llm()
    
    # Create SQL query writer
    write_query = create_sql_query_chain(llm=llm, db=db)
    
    # Create SQL executor
    execute_query = QuerySQLDatabaseTool(db=db)
    
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
    chain = (
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
    
    return chain


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
        return f"Error querying music database: {str(e)}\n\nPlease try rephrasing your question or make it more specific."


# Export the tool
chinook_sql_tool = query_music_database_tool
