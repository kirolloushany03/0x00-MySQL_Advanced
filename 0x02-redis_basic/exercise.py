#!/usr/bin/env python3
"""
This module provides a Cache class for storing data
in Redis with a randomly generated key.
"""

import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    """
    Cache class for interacting with Redis.
    """

    def __init__(self):
        """
        Initialize the Cache instance.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self,
            key: str,
            fn: Optional[Callable] = None
            ) -> Optional[Union[str, bytes, int, float]]:
        value = self._redis.get(key)
        if value is not None and fn:
            value = fn(key)
        return value

    def get_str(self, key: str) -> Optional[str]:
        '''Retrieve a string from Redis.'''
        return self.get(key, fn=lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> Optional[int]:
        ''' Retrieve an integer from Redis'''
        return self.get(key, fn=int)
