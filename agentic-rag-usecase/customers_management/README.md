# Customer Management Library

A simple Python library for managing customer records in a SQLite database using SQLAlchemy ORM.

## Features

- **CRUD Operations**: Create, Read, Update, Delete customer records
- **Customer Fields**: customer_id, name, address, email, phone, credit, active_status
- **Search & Filter**: Search by name/email, filter by status
- **Credit Management**: Add or subtract customer credit
- **Status Management**: Activate/Deactivate customers
- **Sample Data**: Generate India-based sample customer records

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from customers_management import CustomerManager

# Initialize the manager
manager = CustomerManager("sqlite:///customers.db")

# Create a customer
customer = manager.create_customer(
    name="Rajesh Kumar",
    address="123 MG Road, Mumbai, Maharashtra - 400001",
    email="rajesh.kumar@gmail.com",
    phone="+919876543210",
    credit=5000.0,
    active_status="active"
)

# Get all customers
all_customers = manager.get_all_customers()
for c in all_customers:
    print(c.name, c.email)

# Get customer by ID
customer = manager.get_customer(1)

# Update customer
manager.update_customer(1, name="Rajesh Kumar Sharma", credit=10000.0)

# Update credit
manager.update_credit(1, 500.0)  # Add 500 to credit

# Search customers
results = manager.search_customers("Rajesh")

# Deactivate customer
manager.deactivate_customer(1)

# Delete customer
manager.delete_customer(1)
```

### Generate Sample Data

```python
from customers_management import generate_sample_customers

# Generate 25 India-based sample customers
generate_sample_customers("sqlite:///customers.db", count=25)
```

Or run directly (creates database in `db/` folder):
```bash
python -m customers_management.sample_data
```

## Customer Model

| Field | Type | Description |
|-------|------|-------------|
| customer_id | Integer | Primary key (auto-increment) |
| name | String | Customer name |
| address | String | Customer address |
| email | String | Customer email (unique) |
| phone | String | Customer phone number |
| credit | Float | Customer credit balance |
| active_status | Enum | 'active' or 'inactive' |

## API Reference

### CustomerManager

#### `__init__(db_path="sqlite:///customers.db")`
Initialize the customer manager with a database path.

#### `create_customer(name, address, email, phone, credit=0.0, active_status="active")`
Create a new customer record.

#### `get_customer(customer_id)`
Retrieve a customer by ID.

#### `get_customer_by_email(email)`
Retrieve a customer by email.

#### `get_all_customers()`
Retrieve all customers.

#### `get_active_customers()`
Retrieve only active customers.

#### `update_customer(customer_id, **kwargs)`
Update customer fields.

#### `delete_customer(customer_id)`
Delete a customer record.

#### `update_credit(customer_id, amount)`
Add or subtract from customer credit.

#### `activate_customer(customer_id)`
Set customer status to active.

#### `deactivate_customer(customer_id)`
Set customer status to inactive.

#### `search_customers(search_term)`
Search customers by name or email.

#### `get_customer_count()`
Get total number of customers.

## Running Tests

```bash
cd agentic-rag-usecase
python -m tests.test_customer_management
```

Or using unittest:
```bash
python -m unittest tests.test_customer_management
```

## Project Structure

```
customers_management/
├── __init__.py          # Package initialization
├── models.py            # SQLAlchemy models
├── manager.py           # CustomerManager class
├── sample_data.py       # Sample data generator
└── requirements.txt     # Dependencies

tests/
├── __init__.py
└── test_customer_management.py  # Comprehensive test suite
```

## Requirements

- Python 3.7+
- SQLAlchemy 2.0.23

## License

MIT License
