#!/usr/bin/env python3
"""
This module provides a Cache class for interacting with Redis.
It includes functionality to track method call history and replay it.
"""

import redis
import uuid
from typing import Union, Callable, Optional
import functools


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts how many times a method is called.
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        key = f"{method.__qualname__}"
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator that records the history of inputs and outputs for a method.
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Record the input arguments as a string
        self._redis.rpush(input_key, str(args))

        # Execute the original method and record the output
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))

        return result

    return wrapper


def replay(method: Callable) -> None:
    """
    Displays the history of calls of a particular function.

    Args:
        method: The method whose history will be replayed.
    """
    redis_client = method.__self__._redis
    method_name = method.__qualname__

    # Retrieve the inputs and outputs from Redis
    inputs = redis_client.lrange(f"{method_name}:inputs", 0, -1)
    outputs = redis_client.lrange(f"{method_name}:outputs", 0, -1)

    # Print the number of times the method was called
    print(f"{method_name} was called {len(inputs)} times:")

    # Zip inputs and outputs together and print each pair
    for inp, out in zip(inputs, outputs):
        input_decoded = inp.decode('utf-8')
        output_decoded = out.decode('utf-8')
        print(f"{method_name}(*{input_decoded}) -> {output_decoded}")


class Cache:
    """
    Cache class for storing and retrieving data in Redis with method tracking.
    """

    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis with a randomly generated key.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
        self, key: str, fn: Optional[Callable] = None
    ) -> Optional[Union[str, bytes, int, float]]:
        """
        Retrieve data from Redis and optionally apply a conversion function.
        """
        value = self._redis.get(key)
        if value is not None and fn:
            value = fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string from Redis.
        """
        return self.get(key, fn=lambda x: x.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer from Redis.
        """
        return self.get(key, fn=int)
