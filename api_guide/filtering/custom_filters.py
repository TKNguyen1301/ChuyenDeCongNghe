from rest_framework import filters
from rest_framework.filters import BaseFilterBackend
from django.template import loader
from django.db import models


# =============================================================================
# CUSTOM FILTER BACKENDS
# =============================================================================

class IsOwnerFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    Example from DRF documentation.
    """
    def filter_queryset(self, request, queryset, view):
        """
        Filter queryset to only show objects owned by the current user.
        """
        if request.user.is_authenticated and hasattr(queryset.model, 'owner'):
            return queryset.filter(owner=request.user)
        return queryset


class IsPurchaserFilterBackend(BaseFilterBackend):
    """
    Filter that only allows users to see their own purchases.
    """
    def filter_queryset(self, request, queryset, view):
        """
        Filter queryset to only show purchases made by the current user.
        """
        if request.user.is_authenticated and hasattr(queryset.model, 'purchaser'):
            return queryset.filter(purchaser=request.user)
        return queryset


class PublishedOnlyFilterBackend(BaseFilterBackend):
    """
    Filter that only shows published/active items.
    """
    def filter_queryset(self, request, queryset, view):
        """
        Filter to only show published items.
        """
        # Check for different field names that might indicate published status
        if hasattr(queryset.model, 'in_stock'):
            return queryset.filter(in_stock=True)
        elif hasattr(queryset.model, 'published'):
            return queryset.filter(published=True)
        elif hasattr(queryset.model, 'is_active'):
            return queryset.filter(is_active=True)
        return queryset


class CategoryFilterBackend(BaseFilterBackend):
    """
    Custom filter for category-based filtering with HTML interface.
    """
    category_param = 'category'
    category_title = 'Category'
    category_description = 'Filter by category'

    def filter_queryset(self, request, queryset, view):
        """
        Filter queryset based on category parameter.
        """
        category = request.query_params.get(self.category_param)
        if category and hasattr(queryset.model, 'category'):
            return queryset.filter(category__name__icontains=category)
        return queryset

    def to_html(self, request, queryset, view):
        """
        Render HTML interface for this filter in the browsable API.
        """
        # Get available categories
        if hasattr(queryset.model, 'category'):
            categories = queryset.model.objects.values_list(
                'category__name', flat=True
            ).distinct().order_by('category__name')
        else:
            categories = []

        current_category = request.query_params.get(self.category_param, '')

        template = loader.get_template('rest_framework/filters/category.html')
        context = {
            'param': self.category_param,
            'title': self.category_title,
            'description': self.category_description,
            'categories': categories,
            'current': current_category,
        }
        return template.render(context)


class PriceRangeFilterBackend(BaseFilterBackend):
    """
    Custom filter for price range filtering.
    """
    min_price_param = 'min_price'
    max_price_param = 'max_price'

    def filter_queryset(self, request, queryset, view):
        """
        Filter queryset based on price range.
        """
        min_price = request.query_params.get(self.min_price_param)
        max_price = request.query_params.get(self.max_price_param)

        if hasattr(queryset.model, 'price'):
            if min_price:
                try:
                    min_price = float(min_price)
                    queryset = queryset.filter(price__gte=min_price)
                except ValueError:
                    pass

            if max_price:
                try:
                    max_price = float(max_price)
                    queryset = queryset.filter(price__lte=max_price)
                except ValueError:
                    pass

        return queryset

    def to_html(self, request, queryset, view):
        """
        Render HTML interface for price range filter.
        """
        min_price = request.query_params.get(self.min_price_param, '')
        max_price = request.query_params.get(self.max_price_param, '')

        html = f"""
        <div class="form-group">
            <label>Price Range:</label>
            <div class="row">
                <div class="col-md-6">
                    <input type="number" 
                           name="{self.min_price_param}" 
                           value="{min_price}"
                           placeholder="Min price"
                           class="form-control"
                           step="0.01">
                </div>
                <div class="col-md-6">
                    <input type="number" 
                           name="{self.max_price_param}" 
                           value="{max_price}"
                           placeholder="Max price"
                           class="form-control"
                           step="0.01">
                </div>
            </div>
        </div>
        """
        return html


class DateRangeFilterBackend(BaseFilterBackend):
    """
    Custom filter for date range filtering.
    """
    start_date_param = 'start_date'
    end_date_param = 'end_date'
    date_field = 'created_at'

    def filter_queryset(self, request, queryset, view):
        """
        Filter queryset based on date range.
        """
        start_date = request.query_params.get(self.start_date_param)
        end_date = request.query_params.get(self.end_date_param)

        if hasattr(queryset.model, self.date_field):
            if start_date:
                from django.utils.dateparse import parse_date
                parsed_start = parse_date(start_date)
                if parsed_start:
                    queryset = queryset.filter(**{f'{self.date_field}__date__gte': parsed_start})

            if end_date:
                from django.utils.dateparse import parse_date
                parsed_end = parse_date(end_date)
                if parsed_end:
                    queryset = queryset.filter(**{f'{self.date_field}__date__lte': parsed_end})

        return queryset

    def to_html(self, request, queryset, view):
        """
        Render HTML interface for date range filter.
        """
        start_date = request.query_params.get(self.start_date_param, '')
        end_date = request.query_params.get(self.end_date_param, '')

        html = f"""
        <div class="form-group">
            <label>Date Range:</label>
            <div class="row">
                <div class="col-md-6">
                    <input type="date" 
                           name="{self.start_date_param}" 
                           value="{start_date}"
                           class="form-control"
                           placeholder="Start date">
                </div>
                <div class="col-md-6">
                    <input type="date" 
                           name="{self.end_date_param}" 
                           value="{end_date}"
                           class="form-control"
                           placeholder="End date">
                </div>
            </div>
        </div>
        """
        return html


class StatusFilterBackend(BaseFilterBackend):
    """
    Custom filter for status-based filtering with dropdown.
    """
    status_param = 'status'

    def filter_queryset(self, request, queryset, view):
        """
        Filter queryset based on status.
        """
        status = request.query_params.get(self.status_param)
        if status and hasattr(queryset.model, 'status'):
            return queryset.filter(status=status)
        return queryset

    def to_html(self, request, queryset, view):
        """
        Render HTML dropdown for status filter.
        """
        current_status = request.query_params.get(self.status_param, '')
        
        # Get status choices from model
        status_choices = []
        if hasattr(queryset.model, 'status'):
            field = queryset.model._meta.get_field('status')
            if hasattr(field, 'choices') and field.choices:
                status_choices = field.choices

        options_html = '<option value="">All Statuses</option>'
        for value, label in status_choices:
            selected = 'selected' if value == current_status else ''
            options_html += f'<option value="{value}" {selected}>{label}</option>'

        html = f"""
        <div class="form-group">
            <label for="id_{self.status_param}">Status:</label>
            <select name="{self.status_param}" class="form-control" id="id_{self.status_param}">
                {options_html}
            </select>
        </div>
        """
        return html


class AdvancedSearchFilterBackend(BaseFilterBackend):
    """
    Advanced search filter with multiple field support.
    """
    search_param = 'q'
    search_title = 'Search'
    search_description = 'Search across multiple fields'

    def get_search_fields(self, view):
        """
        Get search fields from view.
        """
        return getattr(view, 'search_fields', [])

    def filter_queryset(self, request, queryset, view):
        """
        Filter queryset based on search query across multiple fields.
        """
        search_query = request.query_params.get(self.search_param)
        if not search_query:
            return queryset

        search_fields = self.get_search_fields(view)
        if not search_fields:
            return queryset

        # Build Q objects for OR search across fields
        from django.db.models import Q
        search_terms = search_query.split()
        
        for term in search_terms:
            queries = Q()
            for field in search_fields:
                # Handle different search types
                if field.startswith('^'):
                    # Starts with
                    field_name = field[1:]
                    queries |= Q(**{f'{field_name}__istartswith': term})
                elif field.startswith('='):
                    # Exact match
                    field_name = field[1:]
                    queries |= Q(**{f'{field_name}__iexact': term})
                elif field.startswith('$'):
                    # Regex search
                    field_name = field[1:]
                    queries |= Q(**{f'{field_name}__iregex': term})
                else:
                    # Default: contains
                    queries |= Q(**{f'{field}__icontains': term})
            
            queryset = queryset.filter(queries)

        return queryset

    def to_html(self, request, queryset, view):
        """
        Render search input HTML.
        """
        search_query = request.query_params.get(self.search_param, '')
        
        html = f"""
        <div class="form-group">
            <label for="id_{self.search_param}">{self.search_title}:</label>
            <input type="text" 
                   name="{self.search_param}" 
                   value="{search_query}"
                   placeholder="{self.search_description}"
                   class="form-control"
                   id="id_{self.search_param}">
        </div>
        """
        return html


# =============================================================================
# COMBINATION FILTER BACKEND
# =============================================================================

class CombinedFilterBackend(BaseFilterBackend):
    """
    A filter backend that combines multiple custom filters.
    """
    def __init__(self):
        self.filters = [
            CategoryFilterBackend(),
            PriceRangeFilterBackend(),
            StatusFilterBackend(),
        ]

    def filter_queryset(self, request, queryset, view):
        """
        Apply all filters in sequence.
        """
        for filter_backend in self.filters:
            queryset = filter_backend.filter_queryset(request, queryset, view)
        return queryset

    def to_html(self, request, queryset, view):
        """
        Combine HTML from all filters.
        """
        html_parts = []
        for filter_backend in self.filters:
            if hasattr(filter_backend, 'to_html'):
                html_parts.append(filter_backend.to_html(request, queryset, view))
        
        return '<div class="combined-filters">' + ''.join(html_parts) + '</div>'