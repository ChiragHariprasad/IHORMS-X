"""
IHORMS-X Database Destroyer
Safely drops all tables and data
"""

from sqlalchemy import create_engine, text
from models import Base
import sys

# Database connection
DATABASE_URL = "postgresql://username:password@localhost:5432/ihorms_db"
engine = create_engine(DATABASE_URL)

def confirm_destruction():
    """Get user confirmation before destroying database"""
    print("=" * 60)
    print("WARNING: DATABASE DESTRUCTION")
    print("=" * 60)
    print("\nThis will PERMANENTLY DELETE all data in the database!")
    print("This action CANNOT be undone.\n")
    
    response = input("Type 'DESTROY' to confirm: ")
    return response == "DESTROY"

def drop_all_tables():
    """Drop all tables in the correct order to handle foreign keys"""
    print("\nDropping all tables...")
    
    try:
        # Drop tables in reverse order of dependencies
        with engine.connect() as conn:
            # Disable foreign key checks temporarily
            conn.execute(text("SET session_replication_role = 'replica';"))
            
            # Get all table names
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            
            tables = [row[0] for row in result]
            
            print(f"Found {len(tables)} tables to drop")
            
            # Drop each table
            for table in tables:
                print(f"  Dropping table: {table}")
                conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            
            # Re-enable foreign key checks
            conn.execute(text("SET session_replication_role = 'origin';"))
            
            conn.commit()
        
        print("\nAll tables dropped successfully!")
        return True
        
    except Exception as e:
        print(f"\nERROR during table drop: {str(e)}")
        return False

def drop_using_metadata():
    """Alternative method using SQLAlchemy metadata"""
    print("\nDropping tables using SQLAlchemy metadata...")
    
    try:
        Base.metadata.drop_all(engine)
        print("All tables dropped successfully using metadata!")
        return True
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return False

def show_database_stats():
    """Show current database statistics before destruction"""
    print("\nCurrent Database Statistics:")
    print("-" * 60)
    
    try:
        with engine.connect() as conn:
            # Get table counts
            result = conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    (xpath('/row/cnt/text()', 
                        xml_count))[1]::text::int as row_count
                FROM (
                    SELECT 
                        schemaname, 
                        tablename, 
                        query_to_xml(
                            format('SELECT COUNT(*) as cnt FROM %I.%I', 
                                schemaname, tablename),
                            false, 
                            true, 
                            ''
                        ) as xml_count
                    FROM pg_tables
                    WHERE schemaname = 'public'
                ) t
                ORDER BY row_count DESC
            """))
            
            total_rows = 0
            for row in result:
                schema, table, count = row
                if count:
                    print(f"  {table}: {count:,} rows")
                    total_rows += count
            
            print("-" * 60)
            print(f"  Total rows across all tables: {total_rows:,}")
            
    except Exception as e:
        print(f"Could not retrieve statistics: {str(e)}")

def main():
    """Main destruction workflow"""
    print("\n" + "=" * 60)
    print("IHORMS-X DATABASE DESTROYER")
    print("=" * 60)
    
    # Show current stats
    show_database_stats()
    
    # Get confirmation
    if not confirm_destruction():
        print("\nDestruction cancelled. Database is safe.")
        sys.exit(0)
    
    print("\nStarting destruction process...")
    
    # Try metadata method first (cleaner)
    success = drop_using_metadata()
    
    # If metadata method fails, try direct SQL
    if not success:
        print("\nTrying alternative method...")
        success = drop_all_tables()
    
    if success:
        print("\n" + "=" * 60)
        print("DATABASE DESTROYED SUCCESSFULLY")
        print("=" * 60)
        print("\nAll tables and data have been permanently removed.")
        print("Run the populator script to recreate the database.")
    else:
        print("\n" + "=" * 60)
        print("DATABASE DESTRUCTION FAILED")
        print("=" * 60)
        print("\nPlease check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()