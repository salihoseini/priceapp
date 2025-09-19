# /price.fiai.ir/app.py

import os
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from flask_swagger_ui import get_swaggerui_blueprint

# Import the extension instances from the new extensions.py file
from extensions import db, login_manager

def create_app(config_object='config.DevelopmentConfig'):
    """
    Application Factory: Creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_object)

    # --- Initialize Extensions ---
    # The instances are now imported, and we initialize them with the app
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # --- Configure Login Manager ---
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from database import User
        return User.query.get(int(user_id))

    # --- Register Blueprints ---
    from admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/AdministratorPanel')

    # --- Setup Swagger UI ---
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'

    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Price Tracker API"}
    )
    app.register_blueprint(swaggerui_blueprint)

    # --- Register Main App Routes ---
    register_main_routes(app)

    return app

def register_main_routes(app):
    """
    Registers the public-facing and API routes directly on the app.
    """
    from services import PriceService, StatsService

    # --- Public Facing Routes ---
    @app.route('/')
    def dashboard():
        return render_template('public/index.html')

    @app.route('/asset/<symbol>')
    def asset_detail(symbol):
        asset_data = PriceService.get_asset_details(symbol)
        if not asset_data:
            return render_template('public/404.html'), 404
        return render_template('public/detail.html', asset=asset_data)

    @app.route('/about')
    def about():
        return render_template('public/about.html')

    @app.route('/contact')
    def contact():
        return render_template('public/contact.html')

    # --- API Endpoints (Optimized) ---
    @app.route('/api/prices/overview')
    def prices_overview():
        """Provides a lightweight overview of all assets for the dashboard."""
        data = PriceService.get_prices_overview()
        return jsonify(data)

    @app.route('/api/prices/detail/<symbol>')
    def price_detail(symbol):
        """Provides detailed price source data for a single asset."""
        data = PriceService.get_price_detail_for_symbol(symbol)
        if not data:
             return jsonify({'error': 'Symbol not found or no active sources'}), 404
        return jsonify(data)

    @app.route('/api/prices/history/<symbol>')
    def price_history(symbol):
        """
        [ENHANCED] Provides historical price data for an asset.
        Accepts 'from', 'to', and 'interval' query parameters.
        """
        from_date = request.args.get('from')
        to_date = request.args.get('to')
        # Default to a 1-hour interval if not specified
        interval = request.args.get('interval', '1h') 

        data = PriceService.get_price_history(
            symbol, 
            from_date_str=from_date, 
            to_date_str=to_date, 
            interval=interval
        )
        # Handle potential errors from the service layer
        if isinstance(data, dict) and 'error' in data:
            return jsonify(data), 400

        return jsonify(data)

    @app.route('/api/stats')
    def market_stats():
        """Provides market highlights (top gainer/loser)."""
        stats = StatsService.get_market_highlights()
        return jsonify(stats)

    # --- SEO and PWA Routes ---
    @app.route('/sitemap.xml')
    def sitemap():
        symbols = PriceService.get_all_active_symbols()
        base_url = request.url_root
        return render_template('public/sitemap.xml', symbols=symbols, base_url=base_url), {'Content-Type': 'application/xml'}

    @app.route('/robots.txt')
    def robots_txt():
        return send_from_directory(app.static_folder, 'robots.txt')
    
    @app.route('/manifest.json')
    def manifest():
        return send_from_directory(app.root_path, 'manifest.json')

    @app.route('/sw.js')
    def service_worker():
        return send_from_directory(app.root_path, 'sw.js')


if __name__ == '__main__':
    app = create_app('config.DevelopmentConfig')
    app.run(debug=True, port=5000)

