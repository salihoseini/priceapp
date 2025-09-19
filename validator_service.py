# /price.fiai.ir/validator_service.py

import time
import datetime
import logging
import os
import numpy as np
from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import func, and_
import json

# Import the application factory and db instance from the main app
from app import create_app, db
from database import ApiSource, PriceHistory, ValidationReport

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Validation Parameters ---
VALIDATION_INTERVAL_MINUTES = 5
STALE_THRESHOLD = 10
IQR_MULTIPLIER = 1.5
MIN_SOURCES_FOR_OUTLIER_CHECK = 4
VOLATILITY_WINDOW_HOURS = 24
VOLATILITY_STD_DEV_THRESHOLD = 5.0
MIN_CHANGES_FOR_VOLATILITY_CHECK = 10
MAX_SINGLE_TICK_PERCENT_CHANGE = 20.0
MAX_UPDATE_LATENCY_HOURS = 2


def run_validation_checks(app):
    """
    Core function to run all data validation checks, manage source visibility,
    and write a report to the ValidationReport table.
    """
    with app.app_context():
        start_time = time.time()
        logging.info("--- Starting data validation run ---")

        visibility_change_log = []

        try:
            # Check all sources that are configured to be active.
            active_sources = db.session.query(ApiSource).filter(ApiSource.is_active == True).all()
            sources_checked_count = len(active_sources)
            if not active_sources:
                logging.info("No active sources to validate. Skipping run.")
                return

            symbols_to_check = defaultdict(list)
            for source in active_sources:
                symbols_to_check[source.symbol].append(source)

            sources_to_hide = set()
            sources_to_show = set()
            now = datetime.datetime.utcnow()

            for symbol, sources in symbols_to_check.items():
                source_names = [s.name for s in sources]
                logging.info(f"Validating {len(source_names)} sources for symbol: {symbol}")

                # --- Run all validation checks ---
                for source in sources:
                    # 1. LATENCY CHECK
                    if source.last_updated and (now - source.last_updated).total_seconds() > MAX_UPDATE_LATENCY_HOURS * 3600:
                        reason = f"Source has not updated in over {MAX_UPDATE_LATENCY_HOURS} hours."
                        logging.warning(f"  > [LATENCY] '{source.name}': {reason}")
                        sources_to_hide.add(source.name)
                        visibility_change_log.append({"source": source.name, "symbol": symbol, "reason": "LATENCY", "action": "HIDE", "details": reason})
                        continue

                    # 2. ZERO/NEGATIVE PRICE CHECK
                    latest_price_entry = db.session.query(PriceHistory.price).filter_by(symbol=symbol, source_name=source.name).order_by(PriceHistory.fetched_at.desc()).first()
                    if latest_price_entry and float(latest_price_entry.price) <= 0:
                        reason = f"Reported a zero or negative price: {latest_price_entry.price}."
                        logging.warning(f"  > [INVALID PRICE] '{source.name}': {reason}")
                        sources_to_hide.add(source.name)
                        visibility_change_log.append({"source": source.name, "symbol": symbol, "reason": "INVALID_PRICE", "action": "HIDE", "details": reason})
                        continue

                    # 3. STALE SOURCE CHECK
                    prices = [float(p[0]) for p in db.session.query(PriceHistory.price).filter_by(symbol=symbol, source_name=source.name).order_by(PriceHistory.fetched_at.desc()).limit(STALE_THRESHOLD).all()]
                    if len(prices) == STALE_THRESHOLD and len(set(prices)) == 1:
                        reason = f"Stuck at price {prices[0]} for {STALE_THRESHOLD} consecutive fetches."
                        logging.warning(f"  > [STALE] '{source.name}': {reason}")
                        sources_to_hide.add(source.name)
                        visibility_change_log.append({"source": source.name, "symbol": symbol, "reason": "STALE", "action": "HIDE", "details": reason})
                        continue

                    # 4. SINGLE-TICK VOLATILITY CHECK
                    last_two = db.session.query(PriceHistory.price).filter_by(symbol=symbol, source_name=source.name).order_by(PriceHistory.fetched_at.desc()).limit(2).all()
                    if len(last_two) == 2:
                        latest_price = float(last_two[0].price)
                        previous_price = float(last_two[1].price)
                        if previous_price > 1e-9:
                            pct_change = (abs(latest_price - previous_price) / previous_price) * 100
                            if pct_change > MAX_SINGLE_TICK_PERCENT_CHANGE:
                                reason = f"Price jumped {pct_change:.2f}% in a single tick."
                                logging.warning(f"  > [TICK VOLATILITY] '{source.name}': {reason}")
                                sources_to_hide.add(source.name)
                                visibility_change_log.append({"source": source.name, "symbol": symbol, "reason": "TICK_VOLATILITY", "action": "HIDE", "details": reason})
                                continue

                # 5. OUTLIER PRICE CHECK (CROSS-SOURCE)
                active_for_symbol = [s.name for s in sources if s.name not in sources_to_hide]
                if len(active_for_symbol) < MIN_SOURCES_FOR_OUTLIER_CHECK:
                    logging.info(f"  > Skipping outlier check for '{symbol}', not enough valid sources.")
                else:
                    subquery = db.session.query(PriceHistory.source_name, func.max(PriceHistory.fetched_at).label('max')).filter(PriceHistory.symbol == symbol, PriceHistory.source_name.in_(active_for_symbol)).group_by(PriceHistory.source_name).subquery()
                    latest = db.session.query(PriceHistory.source_name, PriceHistory.price).join(subquery, and_(PriceHistory.source_name == subquery.c.source_name, PriceHistory.fetched_at == subquery.c.max)).all()
                    latest_prices_dict = {item.source_name: float(item.price) for item in latest}
                    prices_for_iqr = list(latest_prices_dict.values())

                    if len(prices_for_iqr) >= MIN_SOURCES_FOR_OUTLIER_CHECK:
                        q1, q3 = np.percentile(prices_for_iqr, [25, 75])
                        iqr = q3 - q1
                        if iqr > 1e-6:
                            lower = q1 - (IQR_MULTIPLIER * iqr)
                            upper = q3 + (IQR_MULTIPLIER * iqr)
                            for src_name, price in latest_prices_dict.items():
                                if not (lower <= price <= upper):
                                    reason = f"Price {price} was outside the valid range [{lower:.2f} - {upper:.2f}]."
                                    logging.warning(f"  > [OUTLIER] '{src_name}': {reason}")
                                    sources_to_hide.add(src_name)
                                    visibility_change_log.append({"source": src_name, "symbol": symbol, "reason": "OUTLIER", "action": "HIDE", "details": reason})

                # --- Determine which sources passed and should be visible ---
                for source in sources:
                    if source.name not in sources_to_hide:
                        sources_to_show.add(source.name)
                        # If the source was previously hidden, log that it's now visible.
                        if not source.is_visible:
                             visibility_change_log.append({"source": source.name, "symbol": source.symbol, "reason": "PASSED_CHECKS", "action": "SHOW"})

            # 6. --- UPDATE VISIBILITY & REPORT ---
            if sources_to_hide:
                logging.info(f"Hiding {len(sources_to_hide)} sources: {', '.join(sources_to_hide)}")
                db.session.query(ApiSource).filter(ApiSource.name.in_(sources_to_hide)).update({'is_visible': False}, synchronize_session=False)
            
            if sources_to_show:
                logging.info(f"Making {len(sources_to_show)} sources visible: {', '.join(sources_to_show)}")
                db.session.query(ApiSource).filter(ApiSource.name.in_(sources_to_show)).update({'is_visible': True}, synchronize_session=False)

            report = ValidationReport(
                duration_seconds=time.time() - start_time,
                sources_checked_count=sources_checked_count,
                sources_deactivated_count=len(visibility_change_log), # Now tracks total visibility changes
                deactivation_details=visibility_change_log
            )
            db.session.add(report)
            db.session.commit()
            logging.info(f"Validation report saved. {len(visibility_change_log)} visibility changes recorded.")

        except Exception as e:
            logging.error(f"An error occurred during validation run: {e}", exc_info=True)
            db.session.rollback()
        finally:
            logging.info("--- Validation run finished ---")


def main():
    config_name = os.getenv('FLASK_CONFIG', 'config.DevelopmentConfig')
    app = create_app(config_name)
    scheduler = BackgroundScheduler(timezone="UTC")

    logging.info(f"--- Starting Data Validation Service in {config_name.split('.')[-1]} mode ---")
    logging.info(f"Scheduling validation job to run every {VALIDATION_INTERVAL_MINUTES} minutes.")

    scheduler.add_job(run_validation_checks, 'interval', minutes=VALIDATION_INTERVAL_MINUTES, args=[app], id='data_validator_job')
    scheduler.start()
    logging.info("\n--- Scheduler started successfully. Press Ctrl+C to exit. ---")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutdown signal received. Shutting down scheduler...")
        scheduler.shutdown()

if __name__ == "__main__":
    main()

