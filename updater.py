# /price.fiai.ir/updater.py

import requests
import time
import datetime
from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import json
import os

# FIX: Import create_app from app and db from the new central extensions file
from app import create_app
from extensions import db
from database import ApiSource, PriceHistory

# --- Logging Configuration ---
# Provides clear output for the background service
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_price_from_json(data, path):
    """
    Helper function to extract data from nested JSON based on a path array.
    """
    current = data
    for key in path:
        if current is None: return None
        try:
            if isinstance(key, dict):
                search_key, search_value = list(key.items())[0]
                current = next((item for item in current if isinstance(item, dict) and item.get(search_key) == search_value), None)
            else:
                current = current[key]
        except (KeyError, IndexError, TypeError):
            return None
    return current

def process_api_group(app, url, source_ids):
    """
    This function is executed by the scheduler for each unique API endpoint.
    It requires the app instance to create a context for database access.
    """
    with app.app_context():
        try:
            sources = db.session.query(ApiSource).filter(ApiSource.id.in_(source_ids), ApiSource.is_active == True).all()
            if not sources:
                logging.warning(f"No active sources found for job with URL: {url}. Skipping.")
                return

            api_config = sources[0]
            method = api_config.method.upper()
            headers = api_config.headers
            payload = api_config.payload
            
            logging.info(f"Executing job for {url} ({len(sources)} symbols)")

            if method == 'POST':
                response = requests.post(url, headers=headers, json=payload, timeout=20)
            else:
                response = requests.get(url, headers=headers, timeout=20)

            response.raise_for_status()
            data = response.json()
            
            for api_source in sources:
                price = extract_price_from_json(data, api_source.path)
                if price is not None:
                    try:
                        if isinstance(price, str):
                            price = float(price.replace(',', ''))
                        
                        final_price = float(price) * api_source.multiplier

                        new_price_record = PriceHistory(
                            source_name=api_source.name,
                            symbol=api_source.symbol,
                            price=final_price,
                            fetched_at=datetime.datetime.utcnow()
                        )
                        db.session.add(new_price_record)
                        api_source.last_updated = datetime.datetime.utcnow()
                        logging.info(f"  > Stored price for '{api_source.name}': {final_price:.2f}")
                    except (ValueError, TypeError) as e:
                        logging.warning(f"  > Could not process price '{price}' for '{api_source.name}': {e}")
                else:
                    logging.warning(f"  > Price path not found for '{api_source.name}'.")

            db.session.commit()

        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed for URL {url}: {e}")
            db.session.rollback()
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON from {url}: {e}")
            db.session.rollback()
        except Exception as e:
            logging.error(f"An unexpected error occurred for job {url}: {e}")
            db.session.rollback()

def main():
    """
    Main function to start the scheduler.
    """
    # FIX: Changed the default config to DevelopmentConfig for easy local testing.
    # The production environment should set the FLASK_CONFIG env variable to 'config.ProductionConfig'.
    config_name = os.getenv('FLASK_CONFIG', 'config.DevelopmentConfig')
    app = create_app(config_name)
    
    scheduler = BackgroundScheduler(timezone="UTC")
    
    with app.app_context():
        try:
            logging.info(f"--- Starting Intelligent Updater Service in {config_name.split('.')[-1]} mode ---")
            
            active_apis = db.session.query(ApiSource).filter(ApiSource.is_active == True).all()
            if not active_apis:
                logging.warning("No active APIs found. Service will start but no jobs will be scheduled.")
                
            grouped_sources = defaultdict(list)
            for api in active_apis:
                headers_key = frozenset(api.headers.items()) if isinstance(api.headers, dict) else None
                payload_key = frozenset(api.payload.items()) if isinstance(api.payload, dict) else None
                request_key = (api.url, api.method, headers_key, payload_key)
                grouped_sources[request_key].append(api)

            logging.info(f"Found {len(active_apis)} active sources across {len(grouped_sources)} unique API endpoints.")

            for (url, _, _, _), sources_for_url in grouped_sources.items():
                min_interval = min(s.fetch_interval_seconds for s in sources_for_url)
                source_ids = [s.id for s in sources_for_url]
                
                job_id = f"job_{url.replace('://', '_').replace('/', '_').replace('.', '_')}"
                logging.info(f"  - Scheduling job '{job_id}' for URL: {url} to run every {min_interval} seconds.")
                
                scheduler.add_job(
                    process_api_group,
                    'interval',
                    seconds=min_interval,
                    args=[app, url, source_ids],
                    id=job_id
                )
            
            scheduler.start()
            logging.info("\n--- Scheduler started successfully. Press Ctrl+C to exit. ---")

            while True:
                time.sleep(1)

        except (KeyboardInterrupt, SystemExit):
            logging.info("Shutdown signal received. Shutting down scheduler...")
            scheduler.shutdown()
        except Exception as e:
            logging.error(f"A critical error occurred during startup: {e}")

if __name__ == "__main__":
    main()

