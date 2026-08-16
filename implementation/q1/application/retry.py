from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class RetryPolicy:
    def __init__(self, attempts: int, base_delay_seconds: float = 0.15) -> None:
        self._attempts = attempts
        self._base_delay_seconds = base_delay_seconds

    async def run(self, operation: Callable[[], Awaitable[T]]) -> T:
        last_error: Exception | None = None
        for index in range(self._attempts):
            try:
                return await operation()
            except Exception as error:
                last_error = error
                if index == self._attempts - 1:
                    break
                await asyncio.sleep(self._base_delay_seconds * (2**index))
        if last_error is not None:
            raise last_error
        raise RuntimeError("operation failed without captured error")

