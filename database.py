# /price.fiai.ir/database.py

from datetime import datetime
from flask_login import UserMixin

# Import db from the new central extensions.py file
from extensions import db

class User(db.Model, UserMixin):
    """Admin user model for authentication."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class ApiSource(db.Model):
    """Stores configuration for every API endpoint."""
    __tablename__ = 'api_sources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    fa_name = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    url = db.Column(db.String(512), nullable=False)
    display_url = db.Column(db.String(255))
    label = db.Column(db.String(50))
    method = db.Column(db.String(10), default='GET', nullable=False)
    headers = db.Column(db.JSON)
    payload = db.Column(db.JSON)
    path = db.Column(db.JSON, nullable=False)
    multiplier = db.Column(db.Float, default=1.0, nullable=False)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    sort_order = db.Column(db.Integer, default=99, nullable=False)
    fetch_interval_seconds = db.Column(db.Integer, default=300, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_visible = db.Column(db.Boolean, default=True, nullable=False, index=True)
    last_updated = db.Column(db.DateTime)

class PriceHistory(db.Model):
    """Stores every price point fetched from the APIs."""
    __tablename__ = 'price_history'
    id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(100), index=True)
    symbol = db.Column(db.String(20), index=True)
    price = db.Column(db.Float, nullable=False)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class ValidationReport(db.Model):
    """
    Stores a report of each validation run.
    This provides a historical log of the data quality checks.
    """
    __tablename__ = 'validation_reports'
    id = db.Column(db.Integer, primary_key=True)
    run_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    duration_seconds = db.Column(db.Float, nullable=False)
    sources_checked_count = db.Column(db.Integer, nullable=False)
    sources_deactivated_count = db.Column(db.Integer, nullable=False) # Represents visibility changes
    deactivation_details = db.Column(db.JSON)

