import sqlite3
import os

# Use the correct database file as per config.py
db_path = "pickleball_league.db"

if os.path.exists(db_path):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables (excluding SQLite internal tables)
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%';
    """)
    tables = cursor.fetchall()

    if not tables:
        print("⚠ Database is empty (no tables)")
        conn.close()
        exit()

    print(f"Found {len(tables)} tables: {[t[0] for t in tables]}\n")

    # Disable foreign keys temporarily
    cursor.execute("PRAGMA foreign_keys = OFF")

    # Delete in correct dependency order
    delete_order = [
        "matches",
        "fixtures",
        "standings",
        "players",
        "teams",
        "users"
    ]

    for table_name in delete_order:
        try:
            cursor.execute(f"DELETE FROM {table_name}")
            deleted = cursor.rowcount
            print(f"✔ Cleared {table_name}: {deleted} rows deleted")
        except Exception as e:
            print(f"⚠ Error clearing {table_name}: {e}")

    # Re-enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    conn.commit()
    conn.close()

    print("\n Database cleared successfully!")
    print("\nNext steps:")
    print("1. python create_admin.py (create admin user)")
    print("2. Register teams via web interface")
    print("3. Approve teams as admin")
    print("4. Generate fixtures as admin")

else:
    print(" Database file not found")
    print("\nThe database will be created when you start the backend server:")
    print("   python run.py")