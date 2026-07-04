"""Absolute and relative error helpers for comparing approximations."""

import math


def absolute_error(approximate, exact):
    """Return ``|approximate - exact|``."""
    return abs(approximate - exact)


def relative_error(approximate, exact):
    """Return ``|approximate - exact| / |exact|``.

    The relative error is undefined when ``exact`` is zero.  To stay safe we
    return ``0.0`` when the approximation is also zero (a perfect match) and
    ``inf`` otherwise, instead of raising ``ZeroDivisionError``.
    """
    if exact == 0:
        return 0.0 if approximate == 0 else math.inf
    return abs(approximate - exact) / abs(exact)


def error_report(approximate, exact):
    """Bundle the approximation, exact value and both error measures."""
    return {
        "approximate": approximate,
        "exact": exact,
        "absolute_error": absolute_error(approximate, exact),
        "relative_error": relative_error(approximate, exact),
    }
