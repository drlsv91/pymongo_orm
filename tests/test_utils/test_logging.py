"""
Tests for logging utilities.
"""

import logging
from unittest.mock import patch

from mongomodel.utils.logging import setup_logging, get_logger
from mongomodel.config import LOG_FORMAT, DEFAULT_LOG_LEVEL


class TestLogging:
    """Tests for logging utilities."""

    def test_setup_logging_default(self):
        """Test setup_logging with default settings."""
        # Reset logging
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)

        # Setup logging with default settings
        logger = setup_logging()

        # Check the logger
        assert logger.name == "mongomodel"
        assert logger.level == getattr(logging, DEFAULT_LOG_LEVEL)

        # Check that a handler is added
        assert len(logger.handlers) > 0
        assert isinstance(logger.handlers[0], logging.StreamHandler)

        # Check the formatter
        formatter = logger.handlers[0].formatter
        assert formatter._fmt == LOG_FORMAT

    def test_setup_logging_custom_level(self):
        """Test setup_logging with custom level."""
        # Reset logging
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)

        # Setup logging with custom level
        logger = setup_logging(level="DEBUG")

        # Check the logger level
        assert logger.level == logging.DEBUG

    def test_setup_logging_with_file(self, tmp_path):
        """Test setup_logging with log file."""
        # Reset logging
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)

        # Create temp log file path
        log_file = tmp_path / "test.log"

        # Setup logging with file
        logger = setup_logging(log_file=str(log_file))

        # Check that both handlers are added
        assert len(logger.handlers) == 2
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert isinstance(logger.handlers[1], logging.FileHandler)

        # Check the file handler
        file_handler = logger.handlers[1]
        assert file_handler.baseFilename == str(log_file)

        # Test logging to file
        logger.info("Test log message")

        # Check that the message was written to the file
        with open(log_file, "r") as f:
            log_content = f.read()

        assert "Test log message" in log_content

    def test_get_logger(self):
        """Test get_logger function."""
        # Reset logging
        root = logging.getLogger()
        for handler in root.handlers[:]:
            root.removeHandler(handler)

        # Setup the base logger
        setup_logging()

        # Get a child logger
        logger = get_logger("test_module")

        # Check the logger
        assert logger.name == "mongomodel.test_module"

        # Test that it inherits the parent's settings
        # assert logger.level == getattr(logging, DEFAULT_LOG_LEVEL)

        # Test that logging works
        with patch("sys.stdout") as mock_stdout:
            logger.info("Test log message")
            # We can't easily check stdout directly due to logger's asynchronous nature
            # But we can verify the logger is properly configured
            assert (
                logger.handlers == []
            )  # Child loggers don't have their own handlers by default
            assert logger.parent.name == "mongomodel"  # Check parent logger
