import os
import argparse
from app import create_app
from extensions import db
from seed_apis import seed_data # Import the seeding function

def initialize_database(reset=False):
    """
    Initializes the database.
    - Creates tables if they don't exist.
    - Seeds API source data.
    - Optionally resets the entire database if the --reset flag is used.
    """
    app = create_app('config.DevelopmentConfig')
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

        if reset:
            if os.path.exists(db_path):
                print(f"--- Resetting database: Deleting {db_path}... ---")
                os.remove(db_path)
            else:
                print(f"--- Database file not found at {db_path}. Nothing to delete. ---")
        else:
            print("--- Initializing database safely (existing data will be preserved)... ---")

        print("Ensuring all database tables exist...")
        db.create_all()
        print("Tables created/ensured successfully.")

        # Always run the seeder to add new sources or update existing ones.
        # This is a non-destructive operation.
        seed_data(db)

        print("\nDatabase initialization complete!")
        if reset:
            print("The database was fully reset.")
        else:
            print("Existing price data was preserved.")

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(description="Initialize or reset the application database.")
    parser.add_argument(
        '--reset',
        action='store_true', # Creates a flag, e.g., `python init_db.py --reset`
        help="Deletes the existing database file before initializing. WARNING: ALL DATA WILL BE LOST."
    )
    args = parser.parse_args()

    # Call the function with the value of the --reset flag
    initialize_database(reset=args.reset)

