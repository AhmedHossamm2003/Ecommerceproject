"""Pure comparison helpers for configurable quality rules."""

from __future__ import annotations

from decimal import Decimal


def compare_numeric(observed: Decimal, comparison: str, expected: Decimal) -> bool:
    if comparison == "eq":
        return observed == expected
    if comparison == "le":
        return observed <= expected
    if comparison == "ge":
        return observed >= expected
    raise ValueError(f"Unsupported comparison operator: {comparison}")
