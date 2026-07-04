"""Optional exact-value comparison powered by SymPy.

SymPy is used here *only* to check the numerical results, never inside the
numerical methods themselves.  It is an optional dependency: if it is not
installed these helpers raise a clear :class:`SymbolicUnavailable` error so the
rest of CalcLab keeps working.
"""

from .functions import make_function


class SymbolicUnavailable(RuntimeError):
    """Raised when SymPy is requested but not installed."""


def _require_sympy():
    try:
        import sympy
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise SymbolicUnavailable(
            "SymPy is required for --symbolic exact comparison. "
            "Install it with 'pip install sympy'."
        ) from exc
    return sympy


def _parse(sympy, expression):
    # Reuse the strict allow-list parser as a safety gate before handing the
    # text to SymPy, so only vetted expressions ever reach sympify().
    make_function(expression)
    x = sympy.Symbol("x")
    expr = sympy.sympify(expression.replace("^", "**"), locals={"x": x})
    return x, expr


def exact_derivative(expression, x0):
    """Return the exact derivative of ``expression`` evaluated at ``x0``."""
    sympy = _require_sympy()
    x, expr = _parse(sympy, expression)
    return float(sympy.diff(expr, x).subs(x, x0))


def exact_integral(expression, a, b):
    """Return the exact definite integral of ``expression`` over ``[a, b]``."""
    sympy = _require_sympy()
    x, expr = _parse(sympy, expression)
    return float(sympy.integrate(expr, (x, a, b)))
