import logging
import time

from django.db import connection, reset_queries

custom_logger = logging.getLogger("custom_logger")


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        reset_queries()

        # Get beginning stats
        start_queries = len(connection.queries)
        start_time = time.perf_counter()

        # Process the request
        response = self.get_response(request)

        # Get ending stats
        end_time = time.perf_counter()
        end_queries = len(connection.queries)

        # Calculate stats
        total_time = end_time - start_time
        total_queries = end_queries - start_queries

        # Log the results
        # logger = logging.getLogger("debug")
        custom_logger.debug(f"Request: {request.method} {request.path}")
        custom_logger.debug(f"Number of Queries: {total_queries}")
        custom_logger.debug(f"Total time: {(total_time):.2f}s")

        return response
