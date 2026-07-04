"""Numerical differentiation via finite differences.

Every rule estimates the slope ``f'(x)`` from a few nearby function values.
The forward and backward rules have error on the order of ``h`` (first order);
the central rule cancels the leading error term and is second order (``h**2``),
so it is usually the most accurate choice for smooth functions.
"""


def forward_difference(f, x, h):
    r"""Forward difference: ``f'(x) \approx (f(x + h) - f(x)) / h``.  Error O(h)."""
    return (f(x + h) - f(x)) / h


def backward_difference(f, x, h):
    r"""Backward difference: ``f'(x) \approx (f(x) - f(x - h)) / h``.  Error O(h)."""
    return (f(x) - f(x - h)) / h


def central_difference(f, x, h):
    r"""Central difference: ``f'(x) \approx (f(x + h) - f(x - h)) / (2h)``.  Error O(h^2)."""
    return (f(x + h) - f(x - h)) / (2.0 * h)


METHODS = {
    "forward": forward_difference,
    "backward": backward_difference,
    "central": central_difference,
}


def differentiate(f, x, h=1e-5, method="central"):
    """Estimate ``f'(x)`` using the chosen finite-difference ``method``."""
    if h <= 0:
        raise ValueError("Step size h must be positive.")
    try:
        rule = METHODS[method]
    except KeyError:
        raise ValueError(
            f"Unknown method {method!r}. Choose from {sorted(METHODS)}."
        ) from None
    return rule(f, x, h)
