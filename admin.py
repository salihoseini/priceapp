# /price.fiai.ir/admin.py

from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import db # Import the db instance from the main app file
from database import User, ApiSource, PriceHistory
from services import AdminService # To be created later

# Create a Blueprint for the admin panel.
# 'admin' is the name of the blueprint.
# __name__ is the import name.
# template_folder specifies a unique template directory for this blueprint.
admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')


# --- User Authentication Routes ---

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles admin login."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('admin.login'))

        login_user(user, remember=remember)
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    """Handles admin logout."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin.login'))


# --- Admin Dashboard ---

@admin_bp.route('/')
@login_required
def dashboard():
    """Displays the main admin dashboard with key statistics."""
    stats = AdminService.get_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)


# --- API Source Management (CRUD) ---

@admin_bp.route('/sources')
@login_required
def list_sources():
    """Displays all API sources, grouped by symbol."""
    grouped_sources = AdminService.get_grouped_api_sources()
    return render_template('admin/sources.html', grouped_sources=grouped_sources)

@admin_bp.route('/sources/new', methods=['GET', 'POST'])
@login_required
def create_source():
    """Handles the creation of a new API source."""
    if request.method == 'POST':
        # The AdminService will handle the logic of creating the source from form data
        success, message = AdminService.create_source_from_form(request.form)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.list_sources'))
        else:
            flash(message, 'danger')
    
    # Pass an empty source object to the form template
    return render_template('admin/source_form.html', source={})

@admin_bp.route('/sources/edit/<int:source_id>', methods=['GET', 'POST'])
@login_required
def edit_source(source_id):
    """Handles editing an existing API source."""
    source = ApiSource.query.get_or_404(source_id)
    if request.method == 'POST':
        success, message = AdminService.update_source_from_form(source, request.form)
        if success:
            flash(message, 'success')
            return redirect(url_for('admin.list_sources'))
        else:
            flash(message, 'danger')

    return render_template('admin/source_form.html', source=source)

@admin_bp.route('/sources/delete/<int:source_id>', methods=['POST'])
@login_required
def delete_source(source_id):
    """Handles deleting an API source."""
    success, message = AdminService.delete_source_by_id(source_id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('admin.list_sources'))

@admin_bp.route('/sources/reorder', methods=['POST'])
@login_required
def reorder_sources():
    """Handles drag-and-drop reordering of sources via an AJAX call."""
    data = request.get_json()
    success, message = AdminService.reorder_sources(data.get('order'))
    if success:
        return jsonify({'status': 'success', 'message': message})
    else:
        return jsonify({'status': 'error', 'message': message}), 400

@admin_bp.route('/sources/toggle_active/<int:source_id>', methods=['POST'])
@login_required
def toggle_source_active(source_id):
    """Toggles the is_active status of a source."""
    success, new_status = AdminService.toggle_source_status(source_id)
    if success:
        return jsonify({'status': 'success', 'new_status': new_status})
    return jsonify({'status': 'error'}), 400


# --- Price History Management ---

@admin_bp.route('/history')
@login_required
def price_history_management():
    """Displays and filters the price history."""
    page = request.args.get('page', 1, type=int)
    filters = {
        'source_name': request.args.get('source_name', ''),
        'symbol': request.args.get('symbol', ''),
        'start_date': request.args.get('start_date', ''),
        'end_date': request.args.get('end_date', '')
    }
    
    # The AdminService will handle the complex filtering and pagination logic
    pagination = AdminService.get_paginated_price_history(page, filters)
    
    return render_template('admin/history.html', pagination=pagination, filters=filters)

@admin_bp.route('/history/delete_filtered', methods=['POST'])
@login_required
def delete_filtered_history():
    """Deletes price history records based on the current filter criteria."""
    filters = {
        'source_name': request.form.get('source_name', ''),
        'symbol': request.form.get('symbol', ''),
        'start_date': request.form.get('start_date', ''),
        'end_date': request.form.get('end_date', '')
    }
    
    deleted_count, message = AdminService.delete_filtered_history(filters)
    
    flash(f'{deleted_count} records deleted. {message}', 'success')
    return redirect(url_for('admin.price_history_management', **filters))
