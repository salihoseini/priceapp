# /price.fiai.ir/seed_apis.py

from app import db
from database import ApiSource

def seed_data():
    """
    This function synchronizes the database with the complete list of API sources.
    It runs within the Flask application context provided by init_db.py.
    """
    # Define common headers and payload for APIs that require them
    alanchand_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*'
    }
    alanchand_payload = {"lang": "fa"}

    # The complete, authoritative list of all API sources for the project.
    api_definitions = [
        # --- Gold & Coins (Toman) - Sorted by importance ---
        # Sort Order 1-10: Major Coins
        {"name": "alanchand-sekkeh", "symbol": "EGC", "fa_name": "سکه امامی", "unit": "تومان", "url": "https://admin.alanchand.com/api/home", "method": "POST", "headers": alanchand_headers, "payload": alanchand_payload, "path": ["gold", {"slug": "sekkeh"}, "price", 0, "price"], "fetch_interval_seconds": 180, "sort_order": 1, "is_active": True},
        {"name": "daric-egc", "symbol": "EGC", "fa_name": "سکه امامی", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "EGC"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 2, "is_active": True},
        {"name": "daric-ovgc", "symbol": "OVGC", "fa_name": "سکه طرح قدیم", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "OVGC"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 3, "is_active": True},
        {"name": "daric-hcg", "symbol": "HCG", "fa_name": "نیم سکه", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "HCG"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 4, "is_active": True},
        {"name": "daric-qcg", "symbol": "QCG", "fa_name": "ربع سکه", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "QCG"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 5, "is_active": True},
        {"name": "daric-agog", "symbol": "AGOG", "fa_name": "سکه گرمی", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "AGOG"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 6, "is_active": True},
        
        # Sort Order 10-19: Gold by Gram/Mesghal
        {"name": "alanchand-18ayar", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://admin.alanchand.com/api/home", "method": "POST", "headers": alanchand_headers, "payload": alanchand_payload, "path": ["gold", {"slug": "18ayar"}, "price", 0, "price"], "fetch_interval_seconds": 180, "sort_order": 10, "is_active": True},
        {"name": "daric-g18", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "G18"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 11, "is_active": True},
        {"name": "daric-s1", "symbol": "S1", "fa_name": "مثقال", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "S1"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 12, "is_active": True},

        # --- Currencies (Toman) - Sorted by importance ---
        # Sort Order 20-29: Major Currencies
        {"name": "alanchand-usd", "symbol": "USD", "fa_name": "دلار آمریکا", "unit": "تومان", "url": "https://admin.alanchand.com/api/home", "method": "POST", "headers": alanchand_headers, "payload": alanchand_payload, "path": ["arz", {"slug": "usd"}, "price", 0, "price"], "fetch_interval_seconds": 180, "sort_order": 20, "is_active": True},
        {"name": "daric-usd", "symbol": "USD", "fa_name": "دلار آمریکا", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "USD"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 21, "is_active": True},
        {"name": "nobitex", "symbol": "USDT", "fa_name": "تتر", "unit": "تومان", "url": "https://apiv2.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls", "path": ["stats", "usdt-rls", "latest"], "multiplier": 0.1, "fetch_interval_seconds": 60, "sort_order": 22, "is_active": True},
        {"name": "wallex", "symbol": "USDT", "fa_name": "تتر", "unit": "تومان", "url": "https://api.wallex.ir/v1/coin-price-list?keys=USDT", "path": ["result", "markets", 0, "quotes", "TMN", "price"], "fetch_interval_seconds": 60, "sort_order": 23, "is_active": True},
        {"name": "alanchand-eur", "symbol": "EUR", "fa_name": "یورو", "unit": "تومان", "url": "https://admin.alanchand.com/api/home", "method": "POST", "headers": alanchand_headers, "payload": alanchand_payload, "path": ["arz", {"slug": "eur"}, "price", 0, "price"], "fetch_interval_seconds": 180, "sort_order": 24, "is_active": True},
        {"name": "daric-eur", "symbol": "EUR", "fa_name": "یورو", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "EUR"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 25, "is_active": True},
        {"name": "daric-aed", "symbol": "AED", "fa_name": "درهم", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "AED"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 26, "is_active": True},

        # --- Global Commodities (USD) - Sort Order 50+ ---
        {"name": "daric-gop", "symbol": "GOP", "fa_name": "انس جهانی", "unit": "دلار", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "GOP"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 50, "is_active": True},
        {"name": "daric-slv", "symbol": "SLV", "fa_name": "نقره", "unit": "دلار", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "SLV"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 51, "is_active": True},
        
        # --- Other/Legacy Sources - Sort Order 99+ ---
        {"name": "milli", "symbol": "GOLD_18C", "fa_name": "طلای ۱۸ عیار", "unit": "تومان", "url": "https://milli.gold/api/v1/public/milli-price/external", "path": ["price18"], "multiplier": 100, "fetch_interval_seconds": 60, "sort_order": 99, "is_active": True},
        {"name": "wallgold", "symbol": "GOLD_18C", "fa_name": "طلای ۱۸ عیار", "unit": "تومان", "url": "https://api.wallgold.ir/api/v1/price?side=buy&symbol=GLD_18C_750TMN", "path": ["result", "price"], "fetch_interval_seconds": 60, "sort_order": 99, "is_active": True},
        {"name": "taline", "symbol": "GOLD_18C", "fa_name": "طلای ۱۸ عیار", "unit": "تومان", "url": "https://price.tlyn.ir/api/v1/price", "path": ["prices", {"symbol": "GOLD18"}, "price", "buy"], "multiplier": 1000, "fetch_interval_seconds": 120, "sort_order": 99, "is_active": True},
        {"name": "zarpaad", "symbol": "GOLD_18C", "fa_name": "طلای ۱۸ عیار", "unit": "تومان", "url": "https://app.zarpaad.com/api/getGoldBuy", "path": ["data", "gold_buy"], "fetch_interval_seconds": 120, "sort_order": 99, "is_active": True},
        {"name": "melligold", "symbol": "GOLD_18C", "fa_name": "طلای ۱۸ عیار", "unit": "تومان", "url": "https://melligold.com/buying/selling/price/XAU18/", "path": ["price_buy"], "fetch_interval_seconds": 120, "sort_order": 99, "is_active": True},
        {"name": "goldika", "symbol": "GOLD_18C", "fa_name": "طلای ۱۸ عیار", "unit": "تومان", "url": "https://goldika.ir/api/public/price", "path": ["data", "price", "buy"], "multiplier": 0.1, "fetch_interval_seconds": 120, "sort_order": 99, "is_active": True},
        {"name": "technogold", "symbol": "GOLD_18C", "fa_name": "طلای ۱۸ عیار", "unit": "تومان", "url": "https://api.technogold.gold/level/prices?lang=fa", "path": ["data", 0, "buyPrice"], "fetch_interval_seconds": 120, "sort_order": 99, "is_active": True},
    ]

    try:
        print("--- Starting API Source Synchronization ---")
        
        for api_data in api_definitions:
            # Use the app's db.session to query
            source = db.session.query(ApiSource).filter(ApiSource.name == api_data["name"]).first()
            if source:
                print(f"  - Updating '{api_data['name']}'...")
                for key, value in api_data.items():
                    setattr(source, key, value)
            else:
                print(f"  - Adding '{api_data['name']}'")
                source = ApiSource(**api_data)
                # Use the app's db.session to add
                db.session.add(source)

        defined_names = {api['name'] for api in api_definitions}
        sources_to_deactivate = db.session.query(ApiSource).filter(ApiSource.name.notin_(defined_names), ApiSource.is_active == True).all()
        for source in sources_to_deactivate:
            print(f"  - Deactivating '{source.name}' as it is no longer defined.")
            source.is_active = False

        # Use the app's db.session to commit
        db.session.commit()
        print("\n--- API sources synced successfully ---")
    except Exception as e:
        print(f"\nAn error occurred during sync: {e}")
        # Use the app's db.session to rollback
        db.session.rollback()

if __name__ == "__main__":
    # This block allows the script to be run directly for testing,
    # but it's primarily designed to be called by init_db.py
    from app import create_app
    app = create_app('config.DevelopmentConfig')
    with app.app_context():
        seed_data()

