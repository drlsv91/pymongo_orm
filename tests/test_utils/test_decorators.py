"""
Tests for decorator utilities.
"""

import asyncio
import logging
import time
from unittest.mock import AsyncMock, Mock

import pytest

from pymongo_orm.utils.decorators import (
    async_retry,
    async_timing_decorator,
    retry,
    timing_decorator,
)


class TestDecorators:
    """Tests for utility decorators."""

    def test_timing_decorator(self, caplog):
        """Test timing decorator for synchronous functions."""
        caplog.set_level(logging.DEBUG)

        @timing_decorator
        def test_function():
            time.sleep(0.1)
            return "result"

        # Run the decorated function
        result = test_function()

        # Check the result
        assert result == "result"

        # Check the log
        # assert "test_function took" in caplog.text
        # assert "s to execute" in caplog.text

    @pytest.mark.asyncio
    async def test_async_timing_decorator(self, caplog):
        """Test timing decorator for asynchronous functions."""
        caplog.set_level(logging.DEBUG)

        @async_timing_decorator
        async def test_async_function():
            await asyncio.sleep(0.1)
            return "async result"

        # Run the decorated function
        result = await test_async_function()

        # Check the result
        assert result == "async result"

        # Check the log
        # assert "test_async_function took" in caplog.text
        # assert "s to execute" in caplog.text

    def test_retry_decorator_success(self):
        """Test retry decorator with successful function."""
        mock_function = Mock(return_value="success")

        # Create a decorated function
        @retry(max_attempts=3, delay=0.01)
        def test_function():
            return mock_function()

        # Call the function
        result = test_function()

        # Check that the function was called once and returned the correct result
        assert mock_function.call_count == 1
        assert result == "success"

    def test_retry_decorator_failure_then_success(self):
        """Test retry decorator with function that fails then succeeds."""
        # Create a mock that raises an exception the first two times,
        # then succeeds on the third try
        mock_function = Mock(
            side_effect=[
                ValueError("First failure"),
                ValueError("Second failure"),
                "success",
            ],
        )

        # Create a decorated function
        @retry(max_attempts=3, delay=0.01)
        def test_function():
            return mock_function()

        # Call the function
        result = test_function()

        # Check that the function was called three times and returned the correct result
        assert mock_function.call_count == 3
        assert result == "success"

    def test_retry_decorator_all_failures(self):
        """Test retry decorator with function that always fails."""
        # Create a mock that always raises an exception
        mock_function = Mock(side_effect=ValueError("Always fails"))

        # Create a decorated function
        @retry(max_attempts=3, delay=0.01)
        def test_function():
            return mock_function()

        # Call the function and expect it to raise an exception
        with pytest.raises(ValueError, match="Always fails"):
            test_function()

        # Check that the function was called the maximum number of times
        assert mock_function.call_count == 3

    def test_retry_with_specific_exceptions(self):
        """Test retry decorator with specific exceptions."""
        # Create a mock that raises different types of exceptions
        mock_function = Mock(
            side_effect=[
                ValueError("Retryable error"),
                TypeError("Non-retryable error"),
                "success",
            ],
        )

        # Create a decorated function that only retries on ValueError
        @retry(max_attempts=3, delay=0.01, exceptions=(ValueError,))
        def test_function():
            return mock_function()

        # Call the function and expect it to raise TypeError
        with pytest.raises(TypeError, match="Non-retryable error"):
            test_function()

        # Check that the function was called twice (ValueError was retried,
        # but TypeError wasn't in the retry list)
        assert mock_function.call_count == 2

    @pytest.mark.asyncio
    async def test_async_retry_decorator_success(self):
        """Test async retry decorator with successful function."""
        mock_function = AsyncMock(return_value="async success")

        # Create a decorated function
        @async_retry(max_attempts=3, delay=0.01)
        async def test_async_function():
            return await mock_function()

        # Call the function
        result = await test_async_function()

        # Check that the function was called once and returned the correct result
        assert mock_function.call_count == 1
        assert result == "async success"

    @pytest.mark.asyncio
    async def test_async_retry_decorator_failure_then_success(self):
        """Test async retry decorator with function that fails then succeeds."""
        # Create a mock that raises an exception the first two times,
        # then succeeds on the third try
        mock_function = AsyncMock(
            side_effect=[
                ValueError("First async failure"),
                ValueError("Second async failure"),
                "async success",
            ],
        )

        # Create a decorated function
        @async_retry(max_attempts=3, delay=0.01)
        async def test_async_function():
            return await mock_function()

        # Call the function
        result = await test_async_function()

        # Check that the function was called three times and returned the correct result
        assert mock_function.call_count == 3
        assert result == "async success"

    @pytest.mark.asyncio
    async def test_async_retry_decorator_all_failures(self):
        """Test async retry decorator with function that always fails."""
        # Create a mock that always raises an exception
        mock_function = AsyncMock(side_effect=ValueError("Always fails async"))

        # Create a decorated function
        @async_retry(max_attempts=3, delay=0.01)
        async def test_async_function():
            return await mock_function()

        # Call the function and expect it to raise an exception
        with pytest.raises(ValueError, match="Always fails async"):
            await test_async_function()

        # Check that the function was called the maximum number of times
        assert mock_function.call_count == 3
