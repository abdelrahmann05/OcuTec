import os
from database import DB_PATH, init_db

def reset_database():
    # Delete existing database if it exists
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Existing database removed.")
    
    # Create new database with updated schema
    init_db()
    print("New database created with updated schema.")

if __name__ == "__main__":
    reset_database()
