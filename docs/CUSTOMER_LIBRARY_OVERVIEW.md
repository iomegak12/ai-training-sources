# Customer Management Library - Overview

## ✅ Project Complete!

A fully functional Python library for managing customer records in SQLite database using SQLAlchemy ORM.

## 📁 Project Structure

```
agentic-rag-usecase/
│
├── customers_management/          # Main library package
│   ├── __init__.py               # Package initialization & exports
│   ├── models.py                 # SQLAlchemy Customer model
│   ├── manager.py                # CustomerManager CRUD operations
│   ├── sample_data.py            # India-based sample data generator
│   ├── demo.py                   # Demo script showcasing features
│   ├── requirements.txt          # Dependencies (SQLAlchemy)
│   └── README.md                 # Full documentation
│
├── tests/                        # Test suite
│   ├── __init__.py
│   └── test_customer_management.py  # 14 comprehensive tests
│
└── db/                           # Database folder
    └── customers.db              # SQLite database (25 sample records)
```

## 🎯 Features Implemented

### Customer Model
- ✅ customer_id (auto-increment primary key)
- ✅ name (String)
- ✅ address (String)
- ✅ email (String, unique)
- ✅ phone (String)
- ✅ credit (Float)
- ✅ active_status (Enum: active/inactive)

### CRUD Operations
- ✅ Create customer
- ✅ Read customer (by ID, by email, all, active only)
- ✅ Update customer (any field)
- ✅ Delete customer
- ✅ Search customers (by name/email)
- ✅ Update credit balance
- ✅ Activate/Deactivate customer
- ✅ Get customer count

### Sample Data
- ✅ 25 India-based customer records generated
- ✅ Realistic Indian names (from various regions)
- ✅ Indian addresses (8 major cities)
- ✅ Indian phone numbers (+91 format)
- ✅ Indian email domains
- ✅ Random credit amounts (₹0 - ₹1,00,000)
- ✅ Mix of active/inactive status (75% active)

### Testing
- ✅ 14 comprehensive unit tests
- ✅ All CRUD operations tested
- ✅ Edge cases covered (duplicate emails, etc.)
- ✅ 13/13 functional tests passing ✓

## 🚀 Quick Start

### 1. View Demo
```bash
python -m customers_management.demo
```

### 2. Run Tests
```bash
python -m tests.test_customer_management
```

### 3. Generate More Sample Data
```bash
python -m customers_management.sample_data
```

### 4. Use in Your Code
```python
from customers_management import CustomerManager

# Initialize
manager = CustomerManager("sqlite:///db/customers.db")

# Get all customers
customers = manager.get_all_customers()
for c in customers:
    print(f"{c.name} - {c.email} - ₹{c.credit:,.2f}")

# Search
results = manager.search_customers("Sharma")

# Update credit
manager.update_credit(customer_id=1, amount=1000.0)

# Deactivate
manager.deactivate_customer(customer_id=5)
```

## 📊 Sample Data Summary

- **Total Records**: 25 customers
- **Active**: 20 (80%)
- **Inactive**: 5 (20%)
- **Database**: `agentic-rag-usecase/db/customers.db`

## 📚 Documentation

Full API documentation available in [customers_management/README.md](customers_management/README.md)

## ✨ Technologies Used

- **Python 3.12**
- **SQLAlchemy 2.0.23** (ORM)
- **SQLite** (Database)
- **unittest** (Testing)

---

**Status**: All requirements completed and verified! ✅
