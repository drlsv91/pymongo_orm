"""
Decorator utilities for MongoDB ORM.
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar, cast

# Setup logger
logger = logging.getLogger("pymongo_orm.decorators")

F = TypeVar("F", bound=Callable[..., Any])
AsyncF = TypeVar("AsyncF", bound=Callable[..., Any])


def timing_decorator(func: F) -> F:
    """
    Decorator to measure and log function execution time.

    Args:
        func: The function to be timed

    Returns:
        The wrapped function
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"{func.__name__} took {end_time - start_time:.4f}s to execute")
        return result

    return cast(F, wrapper)


def async_timing_decorator(func: AsyncF) -> AsyncF:
    """
    Decorator to measure and log async function execution time.

    Args:
        func: The async function to be timed

    Returns:
        The wrapped async function
    """

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"{func.__name__} took {end_time - start_time:.4f}s to execute")
        return result

    return cast(AsyncF, wrapper)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier
        exceptions: Exceptions to catch and retry

    Returns:
        Decorator function
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            mtries, mdelay = max_attempts, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(
                        f"Exception {e}, retrying {func.__name__} "
                        f"in {mdelay} seconds...",
                    )
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return func(*args, **kwargs)

        return cast(F, wrapper)

    return decorator


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Async retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier
        exceptions: Exceptions to catch and retry

    Returns:
        Decorator function
    """

    def decorator(func: AsyncF) -> AsyncF:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            import asyncio

            mtries, mdelay = max_attempts, delay
            while mtries > 1:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(
                        f"Exception {e}, retrying {func.__name__} "
                        f"in {mdelay} seconds...",
                    )
                    await asyncio.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return await func(*args, **kwargs)

        return cast(AsyncF, wrapper)

    return decorator
