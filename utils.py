# /price.fiai.ir/utils.py

import math

class Pagination:
    """A helper class for paginating SQLAlchemy query objects."""
    def __init__(self, query, page, per_page):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total_count = query.count()
        self.items = query.limit(per_page).offset((page - 1) * per_page).all()

    @property
    def total_pages(self):
        return math.ceil(self.total_count / self.per_page)

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.total_pages

    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None

    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None
