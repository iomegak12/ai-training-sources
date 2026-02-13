"""
Database Initialization for Agentic RAG API

This module handles:
1. CRM database initialization with sample data
2. Chinook database setup (expects chinook.db file in db/ folder)
"""
import os
import random
import shutil
from pathlib import Path
from typing import Optional
from config.settings import settings
from config.logging_config import get_logger
from .manager import CustomerManager

logger = get_logger(__name__)


# Sample data for CRM database (India-based)
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Sai", "Aryan", "Reyansh", "Ayaan",
    "Krishna", "Ishaan", "Shaurya", "Atharv", "Advait", "Pranav", "Aadhya",
    "Ananya", "Diya", "Saanvi", "Pari", "Navya", "Ishita", "Kavya", "Aarohi",
    "Prisha", "Kiara"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Kumar", "Singh", "Gupta", "Reddy", "Nair",
    "Iyer", "Rao", "Mehta", "Shah", "Desai", "Joshi", "Agarwal", "Menon",
    "Pillai", "Chopra", "Malhotra", "Khanna", "Bose", "Das", "Mukherjee", "Chatterjee"
]

INDIAN_CITIES = [
    ("Mumbai", "Maharashtra", ["Andheri", "Bandra", "Powai", "Juhu", "Colaba"]),
    ("Delhi", "Delhi", ["Connaught Place", "Karol Bagh", "Dwarka", "Rohini", "Saket"]),
    ("Bangalore", "Karnataka", ["Koramangala", "Indiranagar", "Whitefield", "HSR Layout", "Jayanagar"]),
    ("Chennai", "Tamil Nadu", ["T Nagar", "Anna Nagar", "Velachery", "Adyar", "Mylapore"]),
    ("Hyderabad", "Telangana", ["Banjara Hills", "Jubilee Hills", "Gachibowli", "Hitech City", "Madhapur"]),
    ("Pune", "Maharashtra", ["Koregaon Park", "Hinjewadi", "Kothrud", "Viman Nagar", "Aundh"]),
    ("Kolkata", "West Bengal", ["Salt Lake", "Park Street", "Ballygunge", "Alipore", "New Town"]),
    ("Ahmedabad", "Gujarat", ["Vastrapur", "Satellite", "Maninagar", "Navrangpura", "Bodakdev"])
]

STREET_NAMES = [
    "MG Road", "Gandhi Street", "Nehru Nagar", "Park Avenue", "Main Road",
    "Station Road", "Church Street", "Brigade Road", "Ring Road", "Link Road"
]


def generate_indian_address() -> str:
    """Generate a random Indian address"""
    city, state, areas = random.choice(INDIAN_CITIES)
    area = random.choice(areas)
    street = random.choice(STREET_NAMES)
    building_no = random.randint(1, 999)
    pin_code = random.randint(100000, 999999)
    
    return f"{building_no}, {street}, {area}, {city}, {state} - {pin_code}"


def generate_indian_phone() -> str:
    """Generate a random Indian phone number"""
    # Indian mobile numbers start with 6-9 and have 10 digits
    first_digit = random.choice([6, 7, 8, 9])
    remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    return f"+91{first_digit}{remaining_digits}"


def generate_email(name: str) -> str:
    """Generate email from name"""
    domains = ["gmail.com", "yahoo.in", "outlook.com", "rediffmail.com", "hotmail.com"]
    clean_name = name.lower().replace(" ", ".")
    random_num = random.randint(1, 999)
    return f"{clean_name}{random_num}@{random.choice(domains)}"


def setup_crm_database(sample_records: int = 25) -> bool:
    """
    Initialize CRM database with schema and sample data
    
    Args:
        sample_records: Number of sample customer records to generate (default: 25)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Setting up CRM database...")
        
        # Get database path from settings
        db_path = settings.crm_database_full_path
        
        # Create db directory if it doesn't exist
        db_dir = db_path.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize CustomerManager (creates tables automatically)
        db_uri = f"sqlite:///{db_path}"
        manager = CustomerManager(db_uri)
        
        # Check if database already has data
        existing_count = manager.get_customer_count()
        if existing_count > 0:
            logger.info(f"CRM database already has {existing_count} customers. Skipping sample data generation.")
            return True
        
        # Generate sample customer records
        logger.info(f"Generating {sample_records} sample customer records...")
        
        created_count = 0
        attempts = 0
        max_attempts = sample_records * 3  # Avoid infinite loop with duplicate emails
        
        while created_count < sample_records and attempts < max_attempts:
            attempts += 1
            
            # Generate random customer data
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            name = f"{first_name} {last_name}"
            
            address = generate_indian_address()
            email = generate_email(name)
            phone = generate_indian_phone()
            credit = round(random.uniform(0, 100000), 2)  # Credit between 0 and 1 lakh
            active_status = random.choice(["active", "active", "active", "inactive"])  # 75% active
            
            # Try to create customer
            customer = manager.create_customer(
                name=name,
                address=address,
                email=email,
                phone=phone,
                credit=credit,
                active_status=active_status
            )
            
            if customer:
                created_count += 1
                if created_count % 10 == 0:
                    logger.info(f"Created {created_count}/{sample_records} customers...")
        
        logger.info(f"✓ CRM database setup complete! Created {created_count} sample customers.")
        logger.info(f"  Database location: {db_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up CRM database: {str(e)}", exc_info=True)
        return False


def setup_chinook_database() -> bool:
    """
    Setup Chinook database (music store)
    
    Expects chinook.db file to be present in workspace's lc-training-data folder.
    If found, copies it to the db/ folder. If already exists in db/, verifies it.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Setting up Chinook database...")
        
        # Get target database path from settings
        target_db_path = settings.chinook_database_full_path
        
        # Create db directory if it doesn't exist
        db_dir = target_db_path.parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if database already exists in target location
        if target_db_path.exists():
            file_size = target_db_path.stat().st_size
            if file_size > 0:
                logger.info(f"✓ Chinook database already exists at {target_db_path} ({file_size:,} bytes)")
                return True
            else:
                logger.warning(f"Chinook database file exists but is empty. Will attempt to copy source.")
        
        # Look for source database in workspace
        workspace_root = Path(__file__).parent.parent.parent
        source_candidates = [
            workspace_root / "lc-training-data" / "chinook.db",
            workspace_root / "lc-training-data" / "Chinook_Sqlite.db",
            workspace_root / "db" / "chinook.db"
        ]
        
        source_db_path = None
        for candidate in source_candidates:
            if candidate.exists() and candidate.stat().st_size > 0:
                source_db_path = candidate
                logger.info(f"Found source Chinook database: {source_db_path}")
                break
        
        if source_db_path is None:
            logger.warning(
                "Chinook database not found in workspace. "
                "Please place chinook.db in lc-training-data/ folder or db/ folder."
            )
            return False
        
        # Copy database file
        logger.info(f"Copying Chinook database from {source_db_path} to {target_db_path}...")
        shutil.copy2(source_db_path, target_db_path)
        
        file_size = target_db_path.stat().st_size
        logger.info(f"✓ Chinook database setup complete! ({file_size:,} bytes)")
        logger.info(f"  Database location: {target_db_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up Chinook database: {str(e)}", exc_info=True)
        return False


def initialize_databases(crm_sample_records: int = 25) -> dict:
    """
    Initialize all databases for the application
    
    Args:
        crm_sample_records: Number of sample CRM records to generate (default: 25)
        
    Returns:
        Dictionary with initialization results for each database
    """
    logger.info("=" * 60)
    logger.info("DATABASE INITIALIZATION")
    logger.info("=" * 60)
    
    results = {
        'crm': False,
        'chinook': False
    }
    
    # Setup CRM database
    results['crm'] = setup_crm_database(sample_records=crm_sample_records)
    
    # Setup Chinook database
    results['chinook'] = setup_chinook_database()
    
    # Summary
    logger.info("=" * 60)
    logger.info("DATABASE INITIALIZATION SUMMARY")
    logger.info(f"  CRM Database: {'✓ SUCCESS' if results['crm'] else '✗ FAILED'}")
    logger.info(f"  Chinook Database: {'✓ SUCCESS' if results['chinook'] else '✗ FAILED'}")
    logger.info("=" * 60)
    
    return results


if __name__ == "__main__":
    """Run database initialization standalone"""
    initialize_databases()
