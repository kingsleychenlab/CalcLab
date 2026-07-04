"""Numerical integration (quadrature) rules built on NumPy arrays.

Each rule splits ``[a, b]`` into ``n`` subintervals of width ``dx = (b - a)/n``
and combines the sampled function values.  Using NumPy arrays keeps the sums
vectorised: the function is evaluated once over the whole grid instead of in a
Python loop.
"""

import numpy as np

from .functions import sample


def _grid(a, b, n):
    """Return the ``n + 1`` evenly spaced nodes and the step ``dx``."""
    if n < 1:
        raise ValueError("Number of subintervals n must be a positive integer.")
    x = np.linspace(a, b, n + 1)
    dx = (b - a) / n
    return x, dx


def left_riemann(f, a, b, n):
    """Left Riemann sum: use the left endpoint of each subinterval."""
    x, dx = _grid(a, b, n)
    return dx * np.sum(sample(f, x[:-1]))


def right_riemann(f, a, b, n):
    """Right Riemann sum: use the right endpoint of each subinterval."""
    x, dx = _grid(a, b, n)
    return dx * np.sum(sample(f, x[1:]))


def midpoint_riemann(f, a, b, n):
    """Midpoint rule: use the middle of each subinterval."""
    x, dx = _grid(a, b, n)
    midpoints = (x[:-1] + x[1:]) / 2.0
    return dx * np.sum(sample(f, midpoints))


def trapezoidal(f, a, b, n):
    """Trapezoidal rule: ``(dx / 2) * [f0 + 2 * sum(f_i) + fn]``."""
    x, dx = _grid(a, b, n)
    y = sample(f, x)
    return (dx / 2.0) * (y[0] + 2.0 * np.sum(y[1:-1]) + y[-1])


def simpson(f, a, b, n):
    """Simpson's rule.  Requires an even number of subintervals ``n``.

    ``(dx / 3) * [f0 + 4 * sum(f_odd) + 2 * sum(f_even) + fn]``.  Because it fits
    a parabola to each pair of subintervals it is *exact* for polynomials up to
    degree three.
    """
    if n % 2 != 0:
        raise ValueError("Simpson's rule requires an even number of subintervals n.")
    x, dx = _grid(a, b, n)
    y = sample(f, x)
    odd = np.sum(y[1:-1:2])   # coefficient 4
    even = np.sum(y[2:-1:2])  # coefficient 2
    return (dx / 3.0) * (y[0] + 4.0 * odd + 2.0 * even + y[-1])


METHODS = {
    "left": left_riemann,
    "right": right_riemann,
    "midpoint": midpoint_riemann,
    "trapezoid": trapezoidal,
    "simpson": simpson,
}


def integrate(f, a, b, n=100, method="trapezoid"):
    """Approximate the definite integral of ``f`` over ``[a, b]``."""
    try:
        rule = METHODS[method]
    except KeyError:
        raise ValueError(
            f"Unknown method {method!r}. Choose from {sorted(METHODS)}."
        ) from None
    return rule(f, a, b, n)
