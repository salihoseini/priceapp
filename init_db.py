# /price.fiai.ir/init_db.py

import os
from app import create_app, db
from seed_apis import seed_data # Import the seeding function

# Get the absolute path of the directory where this script is
basedir = os.path.abspath(os.path.dirname(__file__))
db_file = os.path.join(basedir, 'local_dev.db')

def initialize_database():
    """
    Initializes the database by creating all tables and then seeding it
    with the initial API source data. Deletes the old database file if it exists.
    """
    if os.path.exists(db_file):
        print("Deleting existing database...")
        os.remove(db_file)

    # We need to create an app context to interact with the database
    app = create_app('config.DevelopmentConfig')
    with app.app_context():
        print("Creating all database tables...")
        # The following import is necessary to register the models with SQLAlchemy
        # before create_all() is called.
        import database
        db.create_all()
        print("Database tables created.")
        
        # Now, seed the database with the API sources
        seed_data()
        
        print("\nDatabase initialized and seeded successfully!")

if __name__ == '__main__':
    initialize_database()

