from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    """Paginação padrão para a API"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('page_info', {
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'page_size': self.get_page_size(self.request),
            })
        ]))


class LargeResultsSetPagination(LimitOffsetPagination):
    """Paginação para grandes conjuntos de dados"""
    default_limit = 50
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 200
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            ('pagination_info', {
                'limit': self.limit,
                'offset': self.offset,
                'total_count': self.count,
            })
        ]))


class CursorPaginationCustom(LimitOffsetPagination):
    """Paginação baseada em cursor para dados em tempo real"""
    default_limit = 25
    limit_query_param = 'limit'
    offset_query_param = 'cursor'
    max_limit = 100
    
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next_cursor', self.get_next_link()),
            ('previous_cursor', self.get_previous_link()),
            ('results', data),
            ('cursor_info', {
                'limit': self.limit,
                'current_cursor': self.offset,
                'has_next': bool(self.get_next_link()),
                'has_previous': bool(self.get_previous_link()),
            })
        ])) 