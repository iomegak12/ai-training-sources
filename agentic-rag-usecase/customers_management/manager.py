"""
Customer Manager for CRUD operations on customer records
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any
from .models import Base, Customer, ActiveStatus


class CustomerManager:
    """Manager class to handle all customer-related database operations"""
    
    def __init__(self, db_path: str = "sqlite:///customers.db"):
        """
        Initialize CustomerManager with database connection
        
        Args:
            db_path: Database connection string (default: SQLite database)
        """
        self.engine = create_engine(db_path, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def _get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def create_customer(self, name: str, address: str, email: str, 
                       phone: str, credit: float = 0.0, 
                       active_status: str = "active") -> Optional[Customer]:
        """
        Create a new customer record
        
        Args:
            name: Customer name
            address: Customer address
            email: Customer email (must be unique)
            phone: Customer phone number
            credit: Customer credit balance
            active_status: Customer status ('active' or 'inactive')
            
        Returns:
            Customer object if successful, None otherwise
        """
        session = self._get_session()
        try:
            status = ActiveStatus.ACTIVE if active_status.lower() == "active" else ActiveStatus.INACTIVE
            customer = Customer(
                name=name,
                address=address,
                email=email,
                phone=phone,
                credit=credit,
                active_status=status
            )
            session.add(customer)
            session.commit()
            session.refresh(customer)
            return customer
        except IntegrityError:
            session.rollback()
            return None
        finally:
            session.close()
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """
        Retrieve a customer by ID
        
        Args:
            customer_id: Customer ID to retrieve
            
        Returns:
            Customer object if found, None otherwise
        """
        session = self._get_session()
        try:
            customer = session.query(Customer).filter(Customer.customer_id == customer_id).first()
            if customer:
                # Detach from session to avoid DetachedInstanceError
                session.expunge(customer)
            return customer
        finally:
            session.close()
    
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """
        Retrieve a customer by email
        
        Args:
            email: Customer email to search
            
        Returns:
            Customer object if found, None otherwise
        """
        session = self._get_session()
        try:
            customer = session.query(Customer).filter(Customer.email == email).first()
            if customer:
                session.expunge(customer)
            return customer
        finally:
            session.close()
    
    def get_all_customers(self) -> List[Customer]:
        """
        Retrieve all customers
        
        Returns:
            List of all Customer objects
        """
        session = self._get_session()
        try:
            customers = session.query(Customer).all()
            # Detach all customers from session
            for customer in customers:
                session.expunge(customer)
            return customers
        finally:
            session.close()
    
    def get_active_customers(self) -> List[Customer]:
        """
        Retrieve all active customers
        
        Returns:
            List of active Customer objects
        """
        session = self._get_session()
        try:
            customers = session.query(Customer).filter(
                Customer.active_status == ActiveStatus.ACTIVE
            ).all()
            for customer in customers:
                session.expunge(customer)
            return customers
        finally:
            session.close()
    
    def update_customer(self, customer_id: int, **kwargs) -> Optional[Customer]:
        """
        Update customer information
        
        Args:
            customer_id: ID of customer to update
            **kwargs: Fields to update (name, address, email, phone, credit, active_status)
            
        Returns:
            Updated Customer object if successful, None otherwise
        """
        session = self._get_session()
        try:
            customer = session.query(Customer).filter(Customer.customer_id == customer_id).first()
            if not customer:
                return None
            
            # Update allowed fields
            for key, value in kwargs.items():
                if hasattr(customer, key):
                    if key == 'active_status':
                        value = ActiveStatus.ACTIVE if value.lower() == "active" else ActiveStatus.INACTIVE
                    setattr(customer, key, value)
            
            session.commit()
            session.refresh(customer)
            session.expunge(customer)
            return customer
        except IntegrityError:
            session.rollback()
            return None
        finally:
            session.close()
    
    def delete_customer(self, customer_id: int) -> bool:
        """
        Delete a customer record
        
        Args:
            customer_id: ID of customer to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        session = self._get_session()
        try:
            customer = session.query(Customer).filter(Customer.customer_id == customer_id).first()
            if not customer:
                return False
            
            session.delete(customer)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def update_credit(self, customer_id: int, amount: float) -> Optional[Customer]:
        """
        Update customer credit balance
        
        Args:
            customer_id: Customer ID
            amount: Amount to add (positive) or subtract (negative)
            
        Returns:
            Updated Customer object if successful, None otherwise
        """
        session = self._get_session()
        try:
            customer = session.query(Customer).filter(Customer.customer_id == customer_id).first()
            if not customer:
                return None
            
            customer.credit += amount
            session.commit()
            session.refresh(customer)
            session.expunge(customer)
            return customer
        finally:
            session.close()
    
    def deactivate_customer(self, customer_id: int) -> Optional[Customer]:
        """
        Deactivate a customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Updated Customer object if successful, None otherwise
        """
        return self.update_customer(customer_id, active_status="inactive")
    
    def activate_customer(self, customer_id: int) -> Optional[Customer]:
        """
        Activate a customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Updated Customer object if successful, None otherwise
        """
        return self.update_customer(customer_id, active_status="active")
    
    def search_customers(self, search_term: str) -> List[Customer]:
        """
        Search customers by name or email
        
        Args:
            search_term: Search term to look for in name or email
            
        Returns:
            List of matching Customer objects
        """
        session = self._get_session()
        try:
            customers = session.query(Customer).filter(
                (Customer.name.contains(search_term)) | 
                (Customer.email.contains(search_term))
            ).all()
            for customer in customers:
                session.expunge(customer)
            return customers
        finally:
            session.close()
    
    def get_customer_count(self) -> int:
        """
        Get total number of customers
        
        Returns:
            Total customer count
        """
        session = self._get_session()
        try:
            return session.query(Customer).count()
        finally:
            session.close()
