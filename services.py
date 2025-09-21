# /price.fiai.ir/services.py

from collections import defaultdict
from datetime import datetime, timedelta
import json
from sqlalchemy import func, and_, cast, Integer
from sqlalchemy.sql import func as sqlfunc

# Import db from the new central extensions.py file
from extensions import db
from database import ApiSource, PriceHistory
from utils import Pagination

class PriceService:
    """Handles all business logic related to public price data."""

    @staticmethod
    def get_all_active_symbols():
        """Returns a list of all unique, active, and visible symbols for the sitemap."""
        symbols = db.session.query(ApiSource.symbol).filter(
            ApiSource.is_active == True,
            ApiSource.is_visible == True
        ).distinct().all()
        return [s[0] for s in symbols]

    @staticmethod
    def get_prices_overview():
        """
        [OPTIMIZED] Fetches a lightweight overview for all assets.
        This is ideal for the main dashboard.
        """
        latest_entry_sq = db.session.query(
            PriceHistory.source_name,
            sqlfunc.max(PriceHistory.fetched_at).label('max_fetched_at')
        ).group_by(PriceHistory.source_name).subquery()

        latest_prices_q = db.session.query(
            PriceHistory.price,
            ApiSource.symbol,
            ApiSource.fa_name,
            ApiSource.unit,
            ApiSource.sort_order
        ).join(
            latest_entry_sq,
            and_(
                PriceHistory.source_name == latest_entry_sq.c.source_name,
                PriceHistory.fetched_at == latest_entry_sq.c.max_fetched_at
            )
        ).join(
            ApiSource,
            PriceHistory.source_name == ApiSource.name
        ).filter(
            ApiSource.is_active == True,
            ApiSource.is_visible == True
        )

        latest_prices = latest_prices_q.all()

        yesterday = datetime.utcnow() - timedelta(days=1)
        subquery = db.session.query(
            PriceHistory.symbol,
            sqlfunc.min(PriceHistory.fetched_at).label('min_fetched_at')
        ).filter(PriceHistory.fetched_at >= yesterday).group_by(PriceHistory.symbol).subquery()

        prices_24h_ago_q = db.session.query(
            PriceHistory.symbol,
            sqlfunc.avg(PriceHistory.price).label('avg_price')
        ).join(
            subquery,
            and_(
                PriceHistory.symbol == subquery.c.symbol,
                PriceHistory.fetched_at == subquery.c.min_fetched_at
            )
        ).group_by(PriceHistory.symbol)
        
        prices_24h_ago_map = {
            p.symbol: float(p.avg_price) for p in prices_24h_ago_q.all() if p.avg_price is not None
        }

        grouped_data = defaultdict(lambda: {'total_price': 0, 'count': 0})

        for price_entry in latest_prices:
            symbol_data = grouped_data[price_entry.symbol]
            symbol_data['fa_name'] = price_entry.fa_name
            symbol_data['unit'] = price_entry.unit
            symbol_data['sort_order'] = price_entry.sort_order
            symbol_data['total_price'] += price_entry.price
            symbol_data['count'] += 1

        output = []
        for symbol, data in grouped_data.items():
            avg_price = data['total_price'] / data['count'] if data['count'] > 0 else 0
            price_24h_ago = prices_24h_ago_map.get(symbol)
            
            change_24h = 0
            if price_24h_ago and price_24h_ago > 0:
                change_24h = ((float(avg_price) - price_24h_ago) / price_24h_ago) * 100

            output.append({
                'symbol': symbol,
                'fa_name': data['fa_name'],
                'unit': data['unit'],
                'sort_order': data['sort_order'],
                'average_price': float(avg_price),
                'change_24h': change_24h,
            })
            
        output.sort(key=lambda x: x['sort_order'])
        
        return output

    @staticmethod
    def get_price_detail_for_symbol(symbol):
        """
        [ENRICHED] Fetches detailed price information for a single symbol,
        including labels, links, and comparative analysis data.
        """
        active_sources_for_symbol = ApiSource.query.filter_by(
            symbol=symbol,
            is_active=True,
            is_visible=True
        ).all()
        if not active_sources_for_symbol:
            return None

        latest_entry_sq = db.session.query(
            PriceHistory.source_name,
            sqlfunc.max(PriceHistory.fetched_at).label('max_fetched_at')
        ).group_by(PriceHistory.source_name).subquery()

        latest_prices_q = db.session.query(
            PriceHistory.source_name,
            PriceHistory.price,
            ApiSource.fa_name,
            ApiSource.unit,
            ApiSource.last_updated,
            ApiSource.display_url,
            ApiSource.label
        ).join(
            latest_entry_sq,
            and_(
                PriceHistory.source_name == latest_entry_sq.c.source_name,
                PriceHistory.fetched_at == latest_entry_sq.c.max_fetched_at
            )
        ).join(
            ApiSource,
            PriceHistory.source_name == ApiSource.name
        ).filter(
            ApiSource.is_active == True,
            ApiSource.is_visible == True,
            ApiSource.symbol == symbol
        )

        price_entries = latest_prices_q.all()

        if not price_entries:
            return {
                'symbol': symbol,
                'unit': active_sources_for_symbol[0].unit,
                'average_price': 0,
                'low_price': 0,
                'high_price': 0,
                'sources': []
            }

        min_price = min(entry.price for entry in price_entries)
        max_price = max(entry.price for entry in price_entries)
        total_price = sum(entry.price for entry in price_entries)
        count = len(price_entries)
        unit = price_entries[0].unit
        average_price = total_price / count if count > 0 else 0
        
        sources = []
        for entry in price_entries:
            diff_from_avg = 0
            if average_price > 0:
                diff_from_avg = ((entry.price - average_price) / average_price) * 100

            sources.append({
                'source': entry.source_name,
                'fa_name': entry.fa_name,
                'price': entry.price,
                'last_updated': entry.last_updated.isoformat() if entry.last_updated else None,
                'display_url': entry.display_url,
                'label': entry.label,
                'comparison': {
                    'is_highest': entry.price == max_price,
                    'is_lowest': entry.price == min_price,
                    'diff_from_avg_percent': diff_from_avg
                }
            })
        
        return {
            'symbol': symbol,
            'unit': unit,
            'average_price': average_price,
            'low_price': min_price,
            'high_price': max_price,
            'sources': sources
        }

    @staticmethod
    def get_price_history(symbol, from_date_str=None, to_date_str=None, interval='1h'):
        """
        [ENHANCED] Fetches historical price data with dynamic time ranges and intervals.
        Returns time as a Unix timestamp for frontend flexibility.
        """
        try:
            time_unit = interval[-1].lower()
            value = int(interval[:-1])
            interval_seconds = 0
            if time_unit == 'm':
                interval_seconds = value * 60
            elif time_unit == 'h':
                interval_seconds = value * 3600
            elif time_unit == 'd':
                interval_seconds = value * 86400
            elif time_unit == 'w':
                interval_seconds = value * 604800
            
            if interval_seconds == 0:
                raise ValueError("Invalid time unit in interval.")

        except (ValueError, IndexError):
            return {'error': "Invalid interval format. Use formats like '5m', '1h', '3d', '1w'."}

        unix_ts = cast(sqlfunc.strftime('%s', PriceHistory.fetched_at), Integer)
        time_group = (unix_ts / interval_seconds) * interval_seconds

        query = db.session.query(
            time_group.label('time_group'),
            sqlfunc.avg(PriceHistory.price).label('average_price')
        ).filter(
            PriceHistory.symbol == symbol
        )

        try:
            if from_date_str:
                from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
                query = query.filter(PriceHistory.fetched_at >= from_date)
            
            if to_date_str:
                to_date = datetime.strptime(to_date_str, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(PriceHistory.fetched_at < to_date)
            
            if not from_date_str and not to_date_str:
                time_threshold = datetime.utcnow() - timedelta(days=7)
                query = query.filter(PriceHistory.fetched_at >= time_threshold)

        except ValueError:
            return {'error': 'Invalid date format. Please use YYYY-MM-DD.'}

        history = query.group_by('time_group').order_by('time_group').all()

        return [{'time': r.time_group, 'price': r.average_price} for r in history]
    
    @staticmethod
    def get_asset_details(symbol):
        """Fetches all data needed for the asset detail page."""
        source = ApiSource.query.filter_by(symbol=symbol, is_active=True).first()
        if not source:
            return None
        return {'symbol': symbol, 'fa_name': source.fa_name, 'unit': source.unit}


class StatsService:
    """Handles business logic for market statistics."""

    @staticmethod
    def get_market_highlights():
        """Calculates the top gainer and top loser of the day."""
        overview_data = PriceService.get_prices_overview()
        
        if not overview_data:
            return {'top_gainer': None, 'top_loser': None}

        sorted_by_change = sorted(overview_data, key=lambda x: x['change_24h'], reverse=True)
        
        top_gainer = sorted_by_change[0]
        top_loser = sorted_by_change[-1]

        if top_loser['change_24h'] >= 0:
            top_loser = None

        return {'top_gainer': top_gainer, 'top_loser': top_loser}


class AdminService:
    """Handles all business logic for the Admin Panel."""

    @staticmethod
    def get_dashboard_stats():
        """Gathers statistics for the admin dashboard."""
        total_sources = db.session.query(sqlfunc.count(ApiSource.id)).scalar()
        active_sources = db.session.query(sqlfunc.count(ApiSource.id)).filter(ApiSource.is_active == True).scalar()
        total_price_records = db.session.query(sqlfunc.count(PriceHistory.id)).scalar()
        return {
            'total_sources': total_sources,
            'active_sources': active_sources,
            'total_price_records': f'{total_price_records:,}'
        }

    @staticmethod
    def get_grouped_api_sources():
        """Fetches all API sources and groups them by symbol for display."""
        sources = ApiSource.query.order_by(ApiSource.symbol, ApiSource.sort_order).all()
        grouped = defaultdict(list)
        for source in sources:
            grouped[source.symbol].append(source)
        return dict(sorted(grouped.items()))

    @staticmethod
    def _validate_and_prepare_source_data(form_data):
        """Helper to validate and prepare data from the source form."""
        try:
            if not all([form_data.get('name'), form_data.get('symbol'), form_data.get('url')]):
                 return False, "Name, Symbol, and URL are required fields.", None

            data = {
                'name': form_data.get('name'),
                'fa_name': form_data.get('fa_name'),
                'unit': form_data.get('unit'),
                'url': form_data.get('url'),
                'display_url': form_data.get('display_url'),
                'label': form_data.get('label'),
                'method': form_data.get('method', 'GET'),
                'headers': json.loads(form_data.get('headers')) if form_data.get('headers') else None,
                'payload': json.loads(form_data.get('payload')) if form_data.get('payload') else None,
                'path': json.loads(form_data.get('path')) if form_data.get('path') else None,
                'multiplier': float(form_data.get('multiplier', 1.0)),
                'symbol': form_data.get('symbol'),
                'sort_order': int(form_data.get('sort_order', 99)),
                'fetch_interval_seconds': int(form_data.get('fetch_interval_seconds', 300)),
                'is_active': 'is_active' in form_data,
                'is_visible': 'is_visible' in form_data
            }
            return True, "Validation successful", data
        except (json.JSONDecodeError, ValueError) as e:
            return False, f"Invalid data format: {e}", None
        except Exception as e:
            return False, f"An unexpected error occurred: {e}", None

    @staticmethod
    def create_source_from_form(form_data):
        is_valid, msg, data = AdminService._validate_and_prepare_source_data(form_data)
        if not is_valid:
            return False, msg
        
        new_source = ApiSource(**data)
        db.session.add(new_source)
        db.session.commit()
        return True, f"Source '{new_source.name}' created successfully."

    @staticmethod
    def update_source_from_form(source, form_data):
        is_valid, msg, data = AdminService._validate_and_prepare_source_data(form_data)
        if not is_valid:
            return False, msg

        for key, value in data.items():
            setattr(source, key, value)
        
        db.session.commit()
        return True, f"Source '{source.name}' updated successfully."
    
    @staticmethod
    def delete_source_by_id(source_id):
        source = ApiSource.query.get(source_id)
        if source:
            db.session.delete(source)
            db.session.commit()
            return True, f"Source '{source.name}' has been deleted."
        return False, "Source not. found"

    @staticmethod
    def reorder_sources(order_list):
        if not isinstance(order_list, list):
            return False, "Invalid data format for reordering."
        
        try:
            for index, source_id in enumerate(order_list):
                source = ApiSource.query.get(source_id)
                if source:
                    source.sort_order = index
            db.session.commit()
            return True, "Source order updated."
        except Exception as e:
            db.session.rollback()
            return False, f"Error reordering sources: {e}"

    @staticmethod
    def toggle_source_status(source_id):
        source = ApiSource.query.get(source_id)
        if source:
            source.is_active = not source.is_active
            db.session.commit()
            return True, source.is_active
        return False, None

    @staticmethod
    def get_paginated_price_history(page, filters, per_page=50):
        query = PriceHistory.query

        if filters.get('source_name'):
            query = query.filter(PriceHistory.source_name.ilike(f"%{filters['source_name']}%"))
        if filters.get('symbol'):
            query = query.filter(PriceHistory.symbol.ilike(f"%{filters['symbol']}%"))
        if filters.get('start_date'):
            try:
                start_date = datetime.fromisoformat(filters['start_date'])
                query = query.filter(PriceHistory.fetched_at >= start_date)
            except ValueError:
                pass
        if filters.get('end_date'):
            try:
                end_date = datetime.fromisoformat(filters['end_date'])
                query = query.filter(PriceHistory.fetched_at <= end_date)
            except ValueError:
                pass

        query = query.order_by(PriceHistory.fetched_at.desc())
        
        return Pagination(query, page, per_page)

    @staticmethod
    def delete_filtered_history(filters):
        query = PriceHistory.query

        if filters.get('source_name'):
            query = query.filter(PriceHistory.source_name.ilike(f"%{filters['source_name']}%"))
        if filters.get('symbol'):
            query = query.filter(PriceHistory.symbol.ilike(f"%{filters['symbol']}%"))
        if filters.get('start_date'):
            try:
                start_date = datetime.fromisoformat(filters['start_date'])
                query = query.filter(PriceHistory.fetched_at >= start_date)
            except ValueError:
                pass
        if filters.get('end_date'):
            try:
                end_date = datetime.fromisoformat(filters['end_date'])
                query = query.filter(PriceHistory.fetched_at <= end_date)
            except ValueError:
                pass
        
        try:
            num_deleted = query.delete(synchronize_session=False)
            db.session.commit()
            return num_deleted, ""
        except Exception as e:
            db.session.rollback()
            return 0, f"An error occurred: {e}"

