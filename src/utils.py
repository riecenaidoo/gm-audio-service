"""Commonly used methods and decorators.

Contains the default logging formatter and handler for the project.
"""

import asyncio
import functools
import logging
import typing


FORMATTER = logging.Formatter(
    fmt="%(asctime)s %(levelname)-8s"
    + " [%(funcName)s() in %(name)s:%(lineno)s] %(message)s",
    datefmt="%H:%M:%S",
)
HANDLER = logging.StreamHandler()
HANDLER.setFormatter(FORMATTER)


def to_thread(func: typing.Callable):
    """Wrap a function to run asynchronously in a separate thread."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    return wrapper
