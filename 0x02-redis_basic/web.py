#!/usr/bin/env python3
"""A module with tools for request caching and tracking.
"""
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
"""The module-level Redis instance.
"""


def data_cacher(method: Callable[[str], str]) -> Callable[[str], str]:
    """Caches the output of fetched data and tracks access count.

    Args:
        method (Callable[[str], str]): The function to cache.

    Returns:
        Callable[[str], str]: The wrapped function with caching and tracking.
    """

    @wraps(method)
    def invoker(url: str) -> str:
        """Wrapper function for caching the output and tracking access.

        Args:
            url (str): The URL to fetch and cache.

        Returns:
            str: The cached or fetched HTML content.
        """
        # Track access count
        redis_store.incr(f"count:{url}")

        # Fetch from cache
        result = redis_store.get(f"result:{url}")
        if result:
            return result.decode("utf-8")

        # Fetch from the method and cache
        result = method(url)
        redis_store.setex(f"result:{url}", 10, result)
        return result

    return invoker


@data_cacher
def get_page(url: str) -> str:
    """Returns the content of a URL after caching the request's response,
    and tracking the request.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the URL.
    """
    return requests.get(url).text
