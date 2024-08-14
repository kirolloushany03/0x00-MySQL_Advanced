#!/usr/bin/env python3
"""
Web cache and URL access tracker using Redis.
"""

import requests
import redis
from typing import Callable
import functools


class Cache:
    """Cache class to interact with Redis."""

    def __init__(self):
        """Initialize the connection to the Redis server."""
        self._redis = redis.Redis()

    def cache_result(method: Callable) -> Callable:
        """
        Decorator to cache the result of the function and track access count.
        """

        @functools.wraps(method)
        def wrapper(self, url: str) -> str:
            access_count_key = f"count:{url}"
            self._redis.incr(access_count_key)

            cached_content = self._redis.get(url)
            if cached_content:
                return cached_content.decode("utf-8")

            result = method(self, url)
            self._redis.setex(url, 10, result)

            return result

        return wrapper

    @cache_result
    def get_page(self, url: str) -> str:
        """
        Get the HTML content of a URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: The HTML content of the URL.
        """
        response = requests.get(url)
        return response.text

    def get_count(self, url: str) -> int:
        """
        Get the access count of a URL.

        Args:
            url (str): The URL to get the count for.

        Returns:
            int: The access count.
        """
        count = self._redis.get(f"count:{url}")
        return int(count) if count else 0


if __name__ == "__main__":
    cache = Cache()

    url = "http://slowwly.robertomurray.co.uk"
    print(cache.get_page(url))
    print(f"URL accessed {cache.get_count(url)} times")
