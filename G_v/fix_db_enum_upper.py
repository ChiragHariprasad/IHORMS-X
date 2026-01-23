from sqlalchemy import text
from database import engine

def fix_enum_upper():
    connection = engine.connect()
    connection = connection.execution_options(isolation_level="AUTOCOMMIT")
    
    try:
        print("Attempting to add 'ADMITTED' (uppercase) to appointmentstatus enum...")
        connection.execute(text("ALTER TYPE appointmentstatus ADD VALUE 'ADMITTED'"))
        print("Success!")
    except Exception as e:
        print(f"Operation finished (Check if 'ADMITTED' already exists or error occurred): {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    fix_enum_upper()
