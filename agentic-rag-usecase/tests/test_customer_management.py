"""
Comprehensive test suite for Customer Management Library
"""
import unittest
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from customers_management.manager import CustomerManager
from customers_management.models import Customer, ActiveStatus


class TestCustomerManager(unittest.TestCase):
    """Test cases for CustomerManager"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database"""
        cls.test_db = "sqlite:///test_customers.db"
    
    def setUp(self):
        """Create a fresh database for each test"""
        self.manager = CustomerManager(self.test_db)
        # Clear any existing data
        for customer in self.manager.get_all_customers():
            self.manager.delete_customer(customer.customer_id)
    
    def tearDown(self):
        """Clean up after each test"""
        pass
    
    @classmethod
    def tearDownClass(cls):
        """Remove test database file"""
        db_file = "test_customers.db"
        if os.path.exists(db_file):
            os.remove(db_file)
    
    def test_create_customer(self):
        """Test creating a new customer"""
        customer = self.manager.create_customer(
            name="Rajesh Kumar",
            address="123 MG Road, Mumbai, Maharashtra - 400001",
            email="rajesh.kumar@gmail.com",
            phone="+919876543210",
            credit=5000.0,
            active_status="active"
        )
        
        self.assertIsNotNone(customer)
        self.assertEqual(customer.name, "Rajesh Kumar")
        self.assertEqual(customer.email, "rajesh.kumar@gmail.com")
        self.assertEqual(customer.credit, 5000.0)
        self.assertEqual(customer.active_status, ActiveStatus.ACTIVE)
    
    def test_create_duplicate_email(self):
        """Test that duplicate emails are not allowed"""
        self.manager.create_customer(
            name="Test User 1",
            address="Test Address 1",
            email="test@example.com",
            phone="+919876543210"
        )
        
        # Try to create another customer with same email
        duplicate = self.manager.create_customer(
            name="Test User 2",
            address="Test Address 2",
            email="test@example.com",
            phone="+919876543211"
        )
        
        self.assertIsNone(duplicate)
    
    def test_get_customer(self):
        """Test retrieving a customer by ID"""
        created = self.manager.create_customer(
            name="Priya Sharma",
            address="456 Brigade Road, Bangalore, Karnataka - 560001",
            email="priya.sharma@yahoo.in",
            phone="+918765432109"
        )
        
        retrieved = self.manager.get_customer(created.customer_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.customer_id, created.customer_id)
        self.assertEqual(retrieved.name, "Priya Sharma")
        self.assertEqual(retrieved.email, "priya.sharma@yahoo.in")
    
    def test_get_customer_by_email(self):
        """Test retrieving a customer by email"""
        self.manager.create_customer(
            name="Amit Patel",
            address="789 Satellite Road, Ahmedabad, Gujarat - 380015",
            email="amit.patel@outlook.com",
            phone="+917654321098"
        )
        
        customer = self.manager.get_customer_by_email("amit.patel@outlook.com")
        
        self.assertIsNotNone(customer)
        self.assertEqual(customer.name, "Amit Patel")
    
    def test_get_all_customers(self):
        """Test retrieving all customers"""
        # Create multiple customers
        self.manager.create_customer("Customer 1", "Address 1", "c1@test.com", "+919876543210")
        self.manager.create_customer("Customer 2", "Address 2", "c2@test.com", "+919876543211")
        self.manager.create_customer("Customer 3", "Address 3", "c3@test.com", "+919876543212")
        
        all_customers = self.manager.get_all_customers()
        
        self.assertEqual(len(all_customers), 3)
    
    def test_get_active_customers(self):
        """Test retrieving only active customers"""
        self.manager.create_customer("Active 1", "Addr 1", "a1@test.com", "+919876543210", active_status="active")
        self.manager.create_customer("Active 2", "Addr 2", "a2@test.com", "+919876543211", active_status="active")
        self.manager.create_customer("Inactive 1", "Addr 3", "i1@test.com", "+919876543212", active_status="inactive")
        
        active_customers = self.manager.get_active_customers()
        
        self.assertEqual(len(active_customers), 2)
        for customer in active_customers:
            self.assertEqual(customer.active_status, ActiveStatus.ACTIVE)
    
    def test_update_customer(self):
        """Test updating customer information"""
        customer = self.manager.create_customer(
            name="Original Name",
            address="Original Address",
            email="original@test.com",
            phone="+919876543210"
        )
        
        updated = self.manager.update_customer(
            customer.customer_id,
            name="Updated Name",
            phone="+918765432109"
        )
        
        self.assertIsNotNone(updated)
        self.assertEqual(updated.name, "Updated Name")
        self.assertEqual(updated.phone, "+918765432109")
        self.assertEqual(updated.address, "Original Address")  # Unchanged
    
    def test_delete_customer(self):
        """Test deleting a customer"""
        customer = self.manager.create_customer(
            name="To Delete",
            address="Delete Address",
            email="delete@test.com",
            phone="+919876543210"
        )
        
        result = self.manager.delete_customer(customer.customer_id)
        self.assertTrue(result)
        
        # Verify deletion
        deleted = self.manager.get_customer(customer.customer_id)
        self.assertIsNone(deleted)
    
    def test_update_credit(self):
        """Test updating customer credit"""
        customer = self.manager.create_customer(
            name="Credit Test",
            address="Test Address",
            email="credit@test.com",
            phone="+919876543210",
            credit=1000.0
        )
        
        # Add credit
        updated = self.manager.update_credit(customer.customer_id, 500.0)
        self.assertEqual(updated.credit, 1500.0)
        
        # Subtract credit
        updated = self.manager.update_credit(customer.customer_id, -300.0)
        self.assertEqual(updated.credit, 1200.0)
    
    def test_activate_deactivate_customer(self):
        """Test activating and deactivating customers"""
        customer = self.manager.create_customer(
            name="Status Test",
            address="Test Address",
            email="status@test.com",
            phone="+919876543210",
            active_status="active"
        )
        
        # Deactivate
        deactivated = self.manager.deactivate_customer(customer.customer_id)
        self.assertEqual(deactivated.active_status, ActiveStatus.INACTIVE)
        
        # Activate
        activated = self.manager.activate_customer(customer.customer_id)
        self.assertEqual(activated.active_status, ActiveStatus.ACTIVE)
    
    def test_search_customers(self):
        """Test searching customers by name or email"""
        self.manager.create_customer("Rahul Sharma", "Address 1", "rahul@test.com", "+919876543210")
        self.manager.create_customer("Priya Sharma", "Address 2", "priya@test.com", "+919876543211")
        self.manager.create_customer("Amit Kumar", "Address 3", "amit@test.com", "+919876543212")
        
        # Search by last name
        results = self.manager.search_customers("Sharma")
        self.assertEqual(len(results), 2)
        
        # Search by email
        results = self.manager.search_customers("rahul")
        self.assertEqual(len(results), 1)
    
    def test_get_customer_count(self):
        """Test getting customer count"""
        initial_count = self.manager.get_customer_count()
        
        self.manager.create_customer("Customer 1", "Address 1", "c1@test.com", "+919876543210")
        self.manager.create_customer("Customer 2", "Address 2", "c2@test.com", "+919876543211")
        
        new_count = self.manager.get_customer_count()
        self.assertEqual(new_count, initial_count + 2)
    
    def test_customer_to_dict(self):
        """Test converting customer to dictionary"""
        customer = self.manager.create_customer(
            name="Dict Test",
            address="Test Address",
            email="dict@test.com",
            phone="+919876543210",
            credit=2500.0,
            active_status="active"
        )
        
        customer_dict = customer.to_dict()
        
        self.assertEqual(customer_dict['name'], "Dict Test")
        self.assertEqual(customer_dict['email'], "dict@test.com")
        self.assertEqual(customer_dict['credit'], 2500.0)
        self.assertEqual(customer_dict['active_status'], "active")
        self.assertIn('customer_id', customer_dict)


class TestSampleData(unittest.TestCase):
    """Test sample data generation"""
    
    def test_generate_sample_customers(self):
        """Test generating sample customer data"""
        from customers_management.sample_data import generate_sample_customers
        
        test_db = "sqlite:///test_sample.db"
        count = generate_sample_customers(db_path=test_db, count=10)
        
        self.assertEqual(count, 10)
        
        # Verify data was created
        manager = CustomerManager(test_db)
        self.assertEqual(manager.get_customer_count(), 10)
        
        # Clean up
        if os.path.exists("test_sample.db"):
            os.remove("test_sample.db")


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("Running Customer Management Library Tests")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCustomerManager))
    suite.addTests(loader.loadTestsFromTestCase(TestSampleData))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
