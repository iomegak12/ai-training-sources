"""
Demo script to showcase Customer Management Library functionality
"""
from pathlib import Path
from customers_management import CustomerManager

def main():
    # Database path in db folder
    db_folder = Path(__file__).parent.parent / "db"
    db_path = f"sqlite:///{db_folder / 'customers.db'}"
    
    # Initialize manager
    manager = CustomerManager(db_path)
    
    print("=" * 70)
    print("CUSTOMER MANAGEMENT LIBRARY - DEMO")
    print("=" * 70)
    print()
    
    # Show total count
    total = manager.get_customer_count()
    print(f"📊 Total Customers: {total}")
    print()
    
    # Show first 5 customers
    print("👥 First 5 Customers:")
    print("-" * 70)
    all_customers = manager.get_all_customers()
    for customer in all_customers[:5]:
        print(f"ID: {customer.customer_id} | {customer.name}")
        print(f"   Email: {customer.email}")
        print(f"   Phone: {customer.phone}")
        print(f"   Credit: ₹{customer.credit:,.2f} | Status: {customer.active_status.value}")
        print()
    
    # Show active vs inactive
    active = manager.get_active_customers()
    print(f"✅ Active Customers: {len(active)}")
    print(f"❌ Inactive Customers: {total - len(active)}")
    print()
    
    # Search demo
    print("🔍 Search Demo - Search for 'Patel':")
    search_results = manager.search_customers("Patel")
    for customer in search_results:
        print(f"   • {customer.name} ({customer.email})")
    print()
    
    # Get specific customer
    if all_customers:
        customer = all_customers[0]
        print(f"👤 Customer Details (ID: {customer.customer_id}):")
        print(f"   Name: {customer.name}")
        print(f"   Address: {customer.address}")
        print(f"   Email: {customer.email}")
        print(f"   Phone: {customer.phone}")
        print(f"   Credit: ₹{customer.credit:,.2f}")
        print(f"   Status: {customer.active_status.value}")
        print()
    
    # CRUD Operations Demo
    print("🔧 CRUD Operations Demo:")
    print("-" * 70)
    
    # Create
    print("1. CREATE - Adding new customer...")
    new_customer = manager.create_customer(
        name="Demo Customer",
        address="123 Test Street, Mumbai, Maharashtra - 400001",
        email="demo@example.com",
        phone="+919999999999",
        credit=1500.0,
        active_status="active"
    )
    if new_customer:
        print(f"   ✓ Created: {new_customer.name} (ID: {new_customer.customer_id})")
    else:
        print("   ✗ Customer already exists")
    print()
    
    # Read
    if new_customer:
        print("2. READ - Retrieving customer...")
        retrieved = manager.get_customer(new_customer.customer_id)
        print(f"   ✓ Retrieved: {retrieved.name}")
        print()
        
        # Update
        print("3. UPDATE - Updating credit balance...")
        updated = manager.update_credit(new_customer.customer_id, 500.0)
        print(f"   ✓ New Credit: ₹{updated.credit:,.2f}")
        print()
        
        # Delete
        print("4. DELETE - Removing demo customer...")
        deleted = manager.delete_customer(new_customer.customer_id)
        if deleted:
            print(f"   ✓ Deleted successfully")
        print()
    
    print("=" * 70)
    print("Demo completed! Check the README.md for full API documentation.")
    print("=" * 70)


if __name__ == "__main__":
    main()
