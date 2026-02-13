"""
Database models using SQLAlchemy ORM
"""
from sqlalchemy import Column, Integer, String, Float, Enum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

Base = declarative_base()


class ActiveStatus(enum.Enum):
    """Enum for customer active status"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class Customer(Base):
    """Customer model representing customer records in the CRM database"""
    __tablename__ = 'customers'
    
    customer_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), nullable=False)
    credit = Column(Float, default=0.0)
    active_status = Column(Enum(ActiveStatus), default=ActiveStatus.ACTIVE)
    
    def __repr__(self):
        return f"<Customer(id={self.customer_id}, name='{self.name}', email='{self.email}', status='{self.active_status.value}')>"
    
    def to_dict(self):
        """Convert customer object to dictionary"""
        return {
            'customer_id': self.customer_id,
            'name': self.name,
            'address': self.address,
            'email': self.email,
            'phone': self.phone,
            'credit': self.credit,
            'active_status': self.active_status.value
        }
