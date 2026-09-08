"""Formatting helpers for the Streamlit application."""

from __future__ import annotations

import math


def format_number(value: float | int) -> str:
    """Format a numeric value with thousands separators."""
    if value is None:
        return "N/A"

    if isinstance(value, float) and math.isnan(value):
        return "N/A"

    return f"{value:,.2f}"


def format_percent(value: float | int) -> str:
    """Format a percentage value."""
    if value is None:
        return "N/A"

    if isinstance(value, float) and math.isnan(value):
        return "N/A"

    return f"{value:.2f}%"