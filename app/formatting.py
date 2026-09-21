"""Formatting helpers for the Streamlit application."""

from __future__ import annotations

import math


def _is_missing(value: object) -> bool:
    """Return True for values that must not be rendered as a number."""
    if value is None:
        return True

    if isinstance(value, float) and not math.isfinite(value):
        return True

    return False


def format_number(value: float | int | None) -> str:
    """Format a numeric value with thousands separators."""
    if _is_missing(value):
        return "N/A"

    return f"{value:,.2f}"


def format_percent(value: float | int | None) -> str:
    """Format a percentage value."""
    if _is_missing(value):
        return "N/A"

    return f"{value:.2f}%"


def format_ratio_as_percent(value: float | int | None) -> str:
    """Format a ratio (such as a coefficient of variation) as a percentage.

    A coefficient of variation is a dimensionless ratio, so ``0.38`` is
    rendered as ``38.01%``. Values already expressed on a 0-100 scale are
    passed through unchanged.
    """
    if _is_missing(value):
        return "N/A"

    if abs(value) <= 1:
        return format_percent(value * 100)

    return format_percent(value)
