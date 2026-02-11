"""
Generate sample customer data for testing (India-based)
"""
import random
from .manager import CustomerManager


# Indian names
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


def generate_indian_address():
    """Generate a random Indian address"""
    city, state, areas = random.choice(INDIAN_CITIES)
    area = random.choice(areas)
    street = random.choice(STREET_NAMES)
    building_no = random.randint(1, 999)
    pin_code = random.randint(100000, 999999)
    
    return f"{building_no}, {street}, {area}, {city}, {state} - {pin_code}"


def generate_indian_phone():
    """Generate a random Indian phone number"""
    # Indian mobile numbers start with 6-9 and have 10 digits
    first_digit = random.choice([6, 7, 8, 9])
    remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(9)])
    return f"+91{first_digit}{remaining_digits}"


def generate_email(name):
    """Generate email from name"""
    domains = ["gmail.com", "yahoo.in", "outlook.com", "rediffmail.com", "hotmail.com"]
    clean_name = name.lower().replace(" ", ".")
    random_num = random.randint(1, 999)
    return f"{clean_name}{random_num}@{random.choice(domains)}"


def generate_sample_customers(db_path: str = "sqlite:///customers.db", count: int = 25):
    """
    Generate sample customer records
    
    Args:
        db_path: Database connection string
        count: Number of sample customers to generate (default: 25)
    """
    manager = CustomerManager(db_path)
    
    print(f"Generating {count} sample customer records...")
    
    created_count = 0
    attempts = 0
    max_attempts = count * 3  # Avoid infinite loop
    
    while created_count < count and attempts < max_attempts:
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
            print(f"  ✓ Created customer {created_count}: {name} ({email})")
    
    print(f"\nSuccessfully created {created_count} sample customers!")
    print(f"Total customers in database: {manager.get_customer_count()}")
    
    return created_count


if __name__ == "__main__":
    import os
    from pathlib import Path
    
    # Create db folder if it doesn't exist
    db_folder = Path(__file__).parent.parent / "db"
    db_folder.mkdir(exist_ok=True)
    
    # Database path in db folder
    db_path = f"sqlite:///{db_folder / 'customers.db'}"
    
    # Generate 25 sample customers
    generate_sample_customers(db_path=db_path, count=25)
