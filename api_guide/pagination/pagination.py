from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param
from collections import OrderedDict


class LargeResultsSetPagination(pagination.PageNumberPagination):
    """
    Custom pagination class for large result sets.
    Example from the documentation.
    """
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class StandardResultsSetPagination(pagination.PageNumberPagination):
    """
    Standard pagination class for regular result sets.
    Example from the documentation.
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CustomPagination(pagination.PageNumberPagination):
    """
    Custom pagination class that modifies the response format.
    Places next and previous links under a nested 'links' key.
    Example from the documentation.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('links', OrderedDict([
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link())
            ])),
            ('count', self.page.paginator.count),
            ('results', data)
        ]))


class LinkHeaderPagination(pagination.PageNumberPagination):
    """
    Custom pagination class that uses HTTP Link header for pagination links.
    Removes pagination links from the response body.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_paginated_response(self, data):
        next_url = self.get_next_link()
        previous_url = self.get_previous_link()
        
        # Build Link header
        link_header = []
        if next_url is not None:
            link_header.append('<%s>; rel="next"' % next_url)
        if previous_url is not None:
            link_header.append('<%s>; rel="prev"' % previous_url)
        
        response = Response({
            'count': self.page.paginator.count,
            'results': data
        })
        
        if link_header:
            response['Link'] = ', '.join(link_header)
        
        return response


class CustomLimitOffsetPagination(pagination.LimitOffsetPagination):
    """
    Custom LimitOffsetPagination with modified parameters.
    """
    default_limit = 50
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 500

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class CustomCursorPagination(pagination.CursorPagination):
    """
    Custom CursorPagination with specific ordering and page size.
    """
    page_size = 25
    ordering = '-created'
    cursor_query_param = 'cursor'
    template = 'rest_framework/pagination/previous_and_next.html'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class ProductCursorPagination(pagination.CursorPagination):
    """
    Cursor pagination specifically for Product model.
    Uses creation timestamp for stable ordering.
    """
    page_size = 20
    ordering = '-created'
    cursor_query_param = 'cursor'


class ArticleCursorPagination(pagination.CursorPagination):
    """
    Cursor pagination for Article model using slug ordering.
    Demonstrates unique field ordering.
    """
    page_size = 15
    ordering = 'slug'  # Unique, unchanging field
    cursor_query_param = 'cursor'


class FlexiblePagination(pagination.PageNumberPagination):
    """
    A flexible pagination class that allows different page sizes
    based on the endpoint or request parameters.
    """
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_page_size(self, request):
        """
        Override to allow dynamic page sizes based on request.
        """
        # Check if a specific page size is requested
        if self.page_size_query_param:
            try:
                page_size = int(request.query_params[self.page_size_query_param])
                if page_size > 0:
                    return min(page_size, self.max_page_size)
            except (KeyError, ValueError):
                pass
        
        # Check for special 'max' value
        if (self.page_size_query_param and 
            request.query_params.get(self.page_size_query_param) == 'max'):
            return self.max_page_size
        
        return self.page_size


class HeaderPagination(pagination.BasePagination):
    """
    Custom pagination that only uses headers for pagination info.
    No pagination data in response body.
    """
    page_size = 100
    page_query_param = 'page'

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_number = request.query_params.get(self.page_query_param, 1)
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1

        # Calculate offset
        offset = (page_number - 1) * self.page_size
        limit = offset + self.page_size

        # Store pagination info for headers
        self.count = queryset.count()
        self.offset = offset
        self.limit = limit
        self.page_number = page_number
        self.request = request

        return list(queryset[offset:limit])

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object.
        Only includes data, pagination info is in headers.
        """
        # Calculate pagination values
        total_pages = (self.count + self.page_size - 1) // self.page_size
        has_next = self.page_number < total_pages
        has_previous = self.page_number > 1

        response = Response(data)
        
        # Add pagination headers
        response['X-Total-Count'] = str(self.count)
        response['X-Page-Number'] = str(self.page_number)
        response['X-Page-Size'] = str(self.page_size)
        response['X-Total-Pages'] = str(total_pages)
        response['X-Has-Next'] = str(has_next).lower()
        response['X-Has-Previous'] = str(has_previous).lower()

        return response