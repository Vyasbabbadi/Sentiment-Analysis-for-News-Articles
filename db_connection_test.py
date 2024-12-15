import sqlite3
import os

def test_database_connection(db_path='article_analysis.db'):
    # Checking if database file exists
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist!")
        return False

    try:
        # Attempt to connect the database with the model
        conn = sqlite3.connect(db_path)
        
        cursor = conn.cursor()
        
        # Comprehensive connection test
        print("Connection Tests:")
        
        # 1. SQLite Version
        cursor.execute('SELECT SQLITE_VERSION()')
        version = cursor.fetchone()
        print(f"1. SQLite Version: {version[0]}")
        
        # 2. Check existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n2. Existing Tables:")
        if tables:
            for table in tables:
                print(f"   - {table[0]}")
                
                # Count rows in each table
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                row_count = cursor.fetchone()[0]
                print(f"     Rows: {row_count}")
        else:
            print("   No tables found!")
        
        # 3. File properties
        file_stats = os.stat(db_path)
        print(f"\n3. Database File Info:")
        print(f"   Size: {file_stats.st_size} bytes")
        print(f"   Created: {os.path.getctime(db_path)}")
        print(f"   Last Modified: {os.path.getmtime(db_path)}")
        
        return True
    
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}")
        return False
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

# Run the test
if __name__ == "__main__":
    test_database_connection()