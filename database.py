# /price.fiai.ir/database.py

import datetime
from extensions import db
from flask_login import UserMixin

# Flask-SQLAlchemy's db.JSON is dialect-aware and handles this correctly.
# It will use the appropriate JSON type for your configured database (e.g., JSONB on PostgreSQL).

class User(db.Model, UserMixin):
    """User model for admin authentication."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

class ApiSource(db.Model):
    """Stores the configuration for each API source."""
    __tablename__ = 'api_sources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    symbol = db.Column(db.String(50), nullable=False, index=True)
    fa_name = db.Column(db.String(100))
    unit = db.Column(db.String(50))
    url = db.Column(db.String(512), nullable=False)
    method = db.Column(db.String(10), nullable=False, default='GET')
    headers = db.Column(db.JSON)
    payload = db.Column(db.JSON)
    path = db.Column(db.JSON, nullable=False)
    multiplier = db.Column(db.Float, default=1.0)
    fetch_interval_seconds = db.Column(db.Integer, default=60)
    sort_order = db.Column(db.Integer, default=99)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_visible = db.Column(db.Boolean, default=True, index=True) # New column for visibility
    last_updated = db.Column(db.DateTime)

class PriceHistory(db.Model):
    """Stores the historical price data fetched from the sources."""
    __tablename__ = 'price_history'
    id = db.Column(db.Integer, primary_key=True)
    source_name = db.Column(db.String(100), db.ForeignKey('api_sources.name'), nullable=False, index=True)
    symbol = db.Column(db.String(50), nullable=False, index=True)
    price = db.Column(db.Numeric(20, 4), nullable=False)
    fetched_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)

class ValidationReport(db.Model):
    """
    Stores a report of each validation run.
    This provides a historical log of the data quality checks.
    """
    __tablename__ = 'validation_reports'
    id = db.Column(db.Integer, primary_key=True)
    run_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)
    duration_seconds = db.Column(db.Float, nullable=False)
    sources_checked_count = db.Column(db.Integer, nullable=False)
    sources_deactivated_count = db.Column(db.Integer, nullable=False) # Represents visibility changes
    deactivation_details = db.Column(db.JSON)

