# /price.fiai.ir/config.py

import os

# Get the base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a_very_secret_key_that_should_be_changed')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Add other default configurations here

class ProductionConfig(Config):
    """Production configuration with your provided database details."""
    SQLALCHEMY_DATABASE_URI = 'postgresql://fiaiir_admin:uIoW!q9TLCh1@127.0.0.1:5432/fiaiir_price_data'


class DevelopmentConfig(Config):
    """Development configuration using a local SQLite database."""
    DEBUG = True
    # Define the path for the SQLite database file
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'local_dev.db')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Use an in-memory SQLite database for tests

