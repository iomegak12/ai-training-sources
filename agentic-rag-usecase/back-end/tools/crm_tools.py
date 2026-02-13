"""
Business Client (CRM) Retrieval Tools for Agentic RAG API
Read-only tools to query business client CRM database
"""
from typing import Optional, List
from langchain_core.tools import tool
from db.manager import CustomerManager
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

# Lazy-loaded CustomerManager instance
_customer_manager: Optional[CustomerManager] = None


def get_customer_manager() -> CustomerManager:
    """
    Get or create CustomerManager instance with configured database path
    
    Returns:
        CustomerManager instance
    """
    global _customer_manager
    
    if _customer_manager is None:
        db_path = settings.crm_database_full_path
        db_uri = f"sqlite:///{db_path}"
        _customer_manager = CustomerManager(db_uri)
        logger.info(f"CustomerManager initialized with database: {db_path}")
    
    return _customer_manager


@tool("get_business_client_by_id")
def get_business_client_by_id_tool(client_id: int) -> str:
    """
    Retrieve a business client's complete details by their client ID (CRM database).
    
    Use this tool when:
    - User asks about a specific business client by ID
    - User wants to look up business client information using an ID number
    - Need to verify business client details for a specific ID
    
    Args:
        client_id: The unique business client ID number (integer)
        
    Returns:
        Complete business client details including name, address, email, phone, credit, and status.
        Returns error message if client not found.
    """
    try:
        manager = get_customer_manager()
        customer = manager.get_customer(client_id)
        
        if customer:
            return f"""Business Client ID: {customer.customer_id}
Name: {customer.name}
Address: {customer.address}
Email: {customer.email}
Phone: {customer.phone}
Credit: ₹{customer.credit:,.2f}
Status: {customer.active_status.value}"""
        else:
            return f"Error: Business client with ID {client_id} not found in the database."
    except Exception as e:
        logger.error(f"Error retrieving business client by ID {client_id}: {str(e)}", exc_info=True)
        return f"Error retrieving business client: {str(e)}"


@tool("get_business_client_by_email")
def get_business_client_by_email_tool(email: str) -> str:
    """
    Retrieve a business client's complete details by their email address (CRM database).
    
    Use this tool when:
    - User asks about a business client by email address
    - Need to find business client information using an email
    - Verifying business client exists with a specific email
    
    Args:
        email: The business client's email address (string)
        
    Returns:
        Complete business client details including ID, name, address, phone, credit, and status.
        Returns error message if client not found.
    """
    try:
        manager = get_customer_manager()
        customer = manager.get_customer_by_email(email)
        
        if customer:
            return f"""Business Client ID: {customer.customer_id}
Name: {customer.name}
Address: {customer.address}
Email: {customer.email}
Phone: {customer.phone}
Credit: ₹{customer.credit:,.2f}
Status: {customer.active_status.value}"""
        else:
            return f"Error: Business client with email '{email}' not found in the database."
    except Exception as e:
        logger.error(f"Error retrieving business client by email {email}: {str(e)}", exc_info=True)
        return f"Error retrieving business client: {str(e)}"


@tool("search_business_clients")
def search_business_clients_tool(search_term: str) -> str:
    """
    Search for business clients by name or email using a search term (CRM database).
    
    Use this tool when:
    - User wants to find business clients by name (partial or full)
    - Need to search for business clients by email pattern
    - User asks "find business clients with name containing..."
    - Looking for business clients matching specific criteria
    
    Args:
        search_term: The term to search for in business client names or emails (string)
        
    Returns:
        List of matching business clients with their complete details.
        Returns message if no matches found or error occurs.
    """
    try:
        manager = get_customer_manager()
        customers = manager.search_customers(search_term)
        
        if not customers:
            return f"No business clients found matching the search term '{search_term}'."
        
        result = f"Found {len(customers)} business client(s) matching '{search_term}':\n\n"
        for i, customer in enumerate(customers, 1):
            result += f"""{i}. Business Client ID: {customer.customer_id}
   Name: {customer.name}
   Email: {customer.email}
   Phone: {customer.phone}
   Address: {customer.address}
   Credit: ₹{customer.credit:,.2f}
   Status: {customer.active_status.value}

"""
        return result.strip()
    except Exception as e:
        logger.error(f"Error searching business clients with term '{search_term}': {str(e)}", exc_info=True)
        return f"Error searching business clients: {str(e)}"


@tool("get_active_business_clients")
def get_active_business_clients_tool() -> str:
    """
    Retrieve a list of all active business clients only (CRM database).
    
    Use this tool when:
    - User asks for active business clients only
    - Need to filter out inactive business clients
    - User wants to know which business clients are currently active
    - Getting list of business clients who can make transactions
    
    Returns:
        List of active business clients with their complete details.
        Returns error message if no active clients found or error occurs.
    """
    try:
        manager = get_customer_manager()
        customers = manager.get_active_customers()
        
        if not customers:
            return "No active business clients found in the database."
        
        result = f"Total Active Business Clients: {len(customers)}\n\n"
        for i, customer in enumerate(customers, 1):
            result += f"""{i}. Business Client ID: {customer.customer_id}
   Name: {customer.name}
   Email: {customer.email}
   Phone: {customer.phone}
   Address: {customer.address}
   Credit: ₹{customer.credit:,.2f}
   Status: {customer.active_status.value}

"""
        return result.strip()
    except Exception as e:
        logger.error(f"Error retrieving active business clients: {str(e)}", exc_info=True)
        return f"Error retrieving active business clients: {str(e)}"


@tool("get_business_client_count")
def get_business_client_count_tool() -> str:
    """
    Get the total number of business clients in the CRM database.
    
    Use this tool when:
    - User asks "how many business clients are there?"
    - Need to know the total business client count
    - User wants CRM database statistics
    - Getting a quick count without full business client details
    
    Returns:
        Total number of business clients in the CRM database.
        Returns error message if error occurs.
    """
    try:
        manager = get_customer_manager()
        count = manager.get_customer_count()
        
        # Also get active/inactive breakdown
        active_count = len(manager.get_active_customers())
        inactive_count = count - active_count
        
        return f"""Total Business Clients: {count}
Active Business Clients: {active_count}
Inactive Business Clients: {inactive_count}"""
    except Exception as e:
        logger.error(f"Error getting business client count: {str(e)}", exc_info=True)
        return f"Error getting business client count: {str(e)}"


def get_all_crm_tools() -> list:
    """
    Get all CRM tools
    
    Returns:
        List of all CRM tools (5 tools)
    """
    tools = [
        get_business_client_by_id_tool,
        get_business_client_by_email_tool,
        search_business_clients_tool,
        get_active_business_clients_tool,
        get_business_client_count_tool
    ]
    
    logger.info(f"✓ Loaded {len(tools)} CRM tools")
    return tools
