"""Logging configuration for the Streamlit application."""

import logging

LOGGER_NAME = "retail_demand_forecasting"


def get_logger() -> logging.Logger:
    """Return the application logger."""
    logger = logging.getLogger(LOGGER_NAME)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger