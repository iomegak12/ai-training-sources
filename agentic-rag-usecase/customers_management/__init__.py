"""
Customer Management Library

A simple library to manage customer records in SQLite database using SQLAlchemy ORM.

Features:
- Create, Read, Update, Delete (CRUD) operations for customers
- Customer fields: customer_id, name, address, email, phone, credit, active_status
- Search and filter customers
- Credit management
- Activate/Deactivate customers
- Sample data generation

Example usage:
    from customers_management import CustomerManager
    
    # Initialize manager
    manager = CustomerManager("sqlite:///customers.db")
    
    # Create a customer
    customer = manager.create_customer(
        name="Rajesh Kumar",
        address="123 MG Road, Mumbai, Maharashtra - 400001",
        email="rajesh@example.com",
        phone="+919876543210",
        credit=5000.0
    )
    
    # Get all customers
    customers = manager.get_all_customers()
    
    # Update credit
    manager.update_credit(customer.customer_id, 1000.0)
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .models import Customer, ActiveStatus
from .manager import CustomerManager
from .sample_data import generate_sample_customers
from .customer_tools import business_client_tools
from .sql_query_tool import chinook_sql_tool

__all__ = [
    'Customer',
    'ActiveStatus',
    'CustomerManager',
    'generate_sample_customers',
    'business_client_tools',
    'chinook_sql_tool'
]
