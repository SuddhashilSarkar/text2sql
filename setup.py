import os
import subprocess
import sys
import venv
import sqlite3

# Function to create a virtual environment
def create_virtualenv():
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        venv.create("venv", with_pip=True)
    else:
        print("Virtual environment already exists.")

# Function to install dependencies from requirements.txt
def install_dependencies():
    if os.path.exists("requirements.txt"):
        print("Installing dependencies from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("No requirements.txt file found. Skipping dependency installation.")

# Function to set up the SQLite database
def setup_database():
    db_path = "mydb.db"
    if not os.path.exists(db_path):
        print(f"Creating database: {db_path}")
        # Connect to the SQLite database (it will create it if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create necessary tables (you can add more tables or schema here)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        );
        """)

        # Commit and close the connection
        conn.commit()
        conn.close()

        print("Database and tables created.")
    else:
        print("Database already exists.")

# Main function to run all setup tasks
def main():
    create_virtualenv()       # Step 1: Create virtual environment
    install_dependencies()    # Step 2: Install dependencies
    setup_database()          # Step 3: Set up SQLite database

    print("Setup completed successfully!")

if __name__ == "__main__":
    main()
