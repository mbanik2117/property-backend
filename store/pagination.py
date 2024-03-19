from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 4  # Set your desired page size
    page_query_param = 'page'
