# /price.fiai.ir/seed_apis.py

from extensions import db
from database import ApiSource

def seed_data():
    """
    Synchronizes the ApiSource table with the definitions below.
    This is the single source of truth for all API configurations.
    """
    alanchand_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/plain, */*'
    }
    alanchand_payload = {"lang": "fa"}

    api_definitions = [
        # --- Gold & Coins (Toman) ---
        {"name": "alanchand-sekkeh", "symbol": "EGC", "fa_name": "سکه امامی", "unit": "تومان", "url": "https://admin.alanchand.com/api/home", "method": "POST", "headers": alanchand_headers, "payload": alanchand_payload, "path": ["gold", {"slug": "sekkeh"}, "price", 0, "price"], "fetch_interval_seconds": 180, "sort_order": 1, "display_url": "alanchand.com", "label": "Market"},
        {"name": "daric-egc", "symbol": "EGC", "fa_name": "سکه امامی", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "EGC"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 2, "display_url": "daric.gold", "label": "Gold Exchange"},
        {"name": "daric-ovgc", "symbol": "OVGC", "fa_name": "سکه طرح قدیم", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "OVGC"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 3, "display_url": "daric.gold", "label": "Gold Exchange"},
        {"name": "daric-hcg", "symbol": "HCG", "fa_name": "نیم سکه", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "HCG"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 4, "display_url": "daric.gold", "label": "Gold Exchange"},
        {"name": "daric-qcg", "symbol": "QCG", "fa_name": "ربع سکه", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "QCG"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 5, "display_url": "daric.gold", "label": "Gold Exchange"},
        {"name": "daric-agog", "symbol": "AGOG", "fa_name": "سکه گرمی", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "AGOG"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 6, "display_url": "daric.gold", "label": "Gold Exchange"},
        {"name": "alanchand-18ayar", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://admin.alanchand.com/api/home", "method": "POST", "headers": alanchand_headers, "payload": alanchand_payload, "path": ["gold", {"slug": "18ayar"}, "price", 0, "price"], "fetch_interval_seconds": 180, "sort_order": 10, "display_url": "alanchand.com", "label": "Market"},
        {"name": "daric-g18", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "G18"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 11, "display_url": "daric.gold", "label": "Gold Exchange"},
        {"name": "daric-s1", "symbol": "S1", "fa_name": "مثقال", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "S1"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 12, "display_url": "daric.gold", "label": "Gold Exchange"},

        # --- Currencies (Toman) ---
        {"name": "alanchand-usd", "symbol": "USD", "fa_name": "دلار آمریکا", "unit": "تومان", "url": "https://admin.alanchand.com/api/home", "method": "POST", "headers": alanchand_headers, "payload": alanchand_payload, "path": ["arz", {"slug": "usd"}, "price", 0, "price"], "fetch_interval_seconds": 180, "sort_order": 20, "display_url": "alanchand.com", "label": "Market"},
        {"name": "daric-usd", "symbol": "USD", "fa_name": "دلار آمریکا", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "USD"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 21, "display_url": "daric.gold", "label": "Gold Exchange"},
        {"name": "nobitex", "symbol": "USDT", "fa_name": "تتر", "unit": "تومان", "url": "https://apiv2.nobitex.ir/market/stats?srcCurrency=usdt&dstCurrency=rls", "path": ["stats", "usdt-rls", "latest"], "multiplier": 0.1, "fetch_interval_seconds": 60, "sort_order": 22, "display_url": "nobitex.ir", "label": "Crypto Exchange"},
        {"name": "wallex", "symbol": "USDT", "fa_name": "تتر", "unit": "تومان", "url": "https://api.wallex.ir/v1/coin-price-list?keys=USDT", "path": ["result", "markets", 0, "quotes", "TMN", "price"], "fetch_interval_seconds": 60, "sort_order": 23, "display_url": "wallex.ir", "label": "Crypto Exchange"},
        {"name": "alanchand-eur", "symbol": "EUR", "fa_name": "یورو", "unit": "تومان", "url": "https://admin.alanchand.com/api/home", "method": "POST", "headers": alanchand_headers, "payload": alanchand_payload, "path": ["arz", {"slug": "eur"}, "price", 0, "price"], "fetch_interval_seconds": 180, "sort_order": 24, "display_url": "alanchand.com", "label": "Market"},
        {"name": "daric-eur", "symbol": "EUR", "fa_name": "یورو", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "EUR"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 25, "display_url": "daric.gold", "label": "Gold Exchange"},
        {"name": "daric-aed", "symbol": "AED", "fa_name": "درهم", "unit": "تومان", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "AED"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 26, "display_url": "daric.gold", "label": "Gold Exchange"},

        # --- Global Commodities (USD) ---
        {"name": "daric-gop", "symbol": "GOP", "fa_name": "انس جهانی", "unit": "دلار", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "GOP"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 50, "display_url": "daric.gold", "label": "Gold Exchange"},
        {"name": "daric-slv", "symbol": "SLV", "fa_name": "نقره", "unit": "دلار", "url": "https://apie.daric.gold/public/general/GetGoldPrice", "path": [{"symbol": "SLV"}, "bestBuy"], "fetch_interval_seconds": 120, "sort_order": 51, "display_url": "daric.gold", "label": "Gold Exchange"},
        
        # --- Other/Legacy Sources - Not visible by default ---
        {"name": "milli", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://milli.gold/api/v1/public/milli-price/external", "path": ["price18"], "multiplier": 100, "fetch_interval_seconds": 60, "sort_order": 99, "is_visible": False, "display_url": "milli.gold", "label": "Legacy"},
        {"name": "wallgold", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://api.wallgold.ir/api/v1/price?side=buy&symbol=GLD_18C_750TMN", "path": ["result", "price"], "fetch_interval_seconds": 60, "sort_order": 99, "is_visible": False, "display_url": "wallgold.ir", "label": "Legacy"},
        {"name": "taline", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://price.tlyn.ir/api/v1/price", "path": ["prices", {"symbol": "GOLD18"}, "price", "buy"], "multiplier": 1000, "fetch_interval_seconds": 120, "sort_order": 99, "is_visible": False, "display_url": "tlyn.ir", "label": "Legacy"},
        {"name": "zarpaad", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://app.zarpaad.com/api/getGoldBuy", "path": ["data", "gold_buy"], "fetch_interval_seconds": 120, "sort_order": 99, "is_visible": False, "display_url": "zarpaad.com", "label": "Legacy"},
        {"name": "melligold", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://melligold.com/buying/selling/price/XAU18/", "path": ["price_buy"], "fetch_interval_seconds": 120, "sort_order": 99, "is_visible": False, "display_url": "melligold.com", "label": "Legacy"},
        {"name": "goldika", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://goldika.ir/api/public/price", "path": ["data", "price", "buy"], "multiplier": 0.1, "fetch_interval_seconds": 120, "sort_order": 99, "is_visible": False, "display_url": "goldika.ir", "label": "Legacy"},
        {"name": "technogold", "symbol": "G18", "fa_name": "طلا ۱۸ عیار", "unit": "تومان", "url": "https://api.technogold.gold/level/prices?lang=fa", "path": ["data", 0, "buyPrice"], "fetch_interval_seconds": 120, "sort_order": 99, "is_visible": False, "display_url": "technogold.gold", "label": "Legacy"},
    ]

    print("--- Starting API Source Synchronization ---")
    
    for api_data in api_definitions:
        source = db.session.query(ApiSource).filter(ApiSource.name == api_data["name"]).first()
        if source:
            print(f"  - Updating '{api_data['name']}'...")
            for key, value in api_data.items():
                setattr(source, key, value)
        else:
            print(f"  - Adding '{api_data['name']}'")
            source = ApiSource(**api_data)
            db.session.add(source)

    defined_names = {api['name'] for api in api_definitions}
    sources_to_deactivate = db.session.query(ApiSource).filter(ApiSource.name.notin_(defined_names), ApiSource.is_active == True).all()
    for source in sources_to_deactivate:
        print(f"  - Deactivating '{source.name}' as it is no longer defined.")
        source.is_active = False

    db.session.commit()
    print("\n--- API sources synced successfully ---")

