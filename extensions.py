# /price.fiai.ir/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

"""
This file is used to instantiate extensions like SQLAlchemy and LoginManager.
By keeping them in a separate file, we prevent circular import errors.
The extensions are initialized here but are configured in the application factory.
"""

db = SQLAlchemy()
login_manager = LoginManager()
