from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

users = session.query(User).all()
with open('credentials.txt', 'w') as f:
    f.write("IHORMS System Credentials\n")
    f.write("=========================\n\n")
    for u in users:
        # Note: passwords in DB are hashed, but since this is a demo/dev environment 
        # populated by populator.py, we know the default passwords used.
        # We'll list the email and role.
        role_label = u.role.value if hasattr(u.role, 'value') else str(u.role)
        f.write(f"Role: {role_label}\n")
        f.write(f"Email: {u.email}\n")
        f.write(f"Name: {u.first_name} {u.last_name}\n")
        f.write("-" * 20 + "\n")

print("Credentials extracted to credentials.txt")
