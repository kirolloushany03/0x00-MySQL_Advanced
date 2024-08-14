#!/usr/bin/env python3
"""
This module provides a function to fetch and cache HTML content from a URL.
"""

import requests
import redis
from typing import Callable
import functools
from datetime import time


def cache_result(method: Callable) -> Callable:
    """
    Decorator to cache the result of the function and track access count.
    """

    @functools.wraps(method)
    def wrapper(url: str) -> str:
        r = redis.Redis()
        access_count_key = f"count:{url}"
        r.incr(access_count_key)

        cached_content = r.get(url)
        if cached_content:
            return cached_content.decode("utf-8")

        result = method(url)
        r.setex(url, 10, result)

        return result

    return wrapper


@cache_result
def get_page(url: str) -> str:
    """
    Fetch the HTML content of a URL and cache it with a 10-second expiration.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the URL.
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    # Test the get_page function
    url = (
        "http://slowwly.robertomurray.co.uk/delay/5000/url/"
        "https://www.example.com"
    )
    print(get_page(url))
    time.sleep(5)
    print(get_page(url))  # This should return the cached result
