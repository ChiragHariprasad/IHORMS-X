from sqlalchemy import text
from database import engine

def check_enum():
    connection = engine.connect()
    try:
        result = connection.execute(text("SELECT unnest(enum_range(NULL::appointmentstatus))")).fetchall()
        print("Enum values in DB:", [row[0] for row in result])
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    check_enum()
