"""Pagination utilities for coderr_app API.

This provides a small page size tuned for the frontend and allows
clients to request a larger page via the `page_size` query param up to
`max_page_size`.
"""

from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """PageNumberPagination with small default page size and client-overridable parameter."""

    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100