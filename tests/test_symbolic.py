"""Tests for the optional SymPy-backed exact comparison.

The whole module is skipped when SymPy is not installed, so a fresh clone
without the optional dependency still passes cleanly.
"""

import math

import pytest

pytest.importorskip("sympy")

from calclab import symbolic


def test_exact_derivative_of_x_squared():
    assert symbolic.exact_derivative("x^2", 3.0) == pytest.approx(6.0)


def test_exact_derivative_of_sin():
    assert symbolic.exact_derivative("sin(x)", 0.0) == pytest.approx(1.0)


def test_exact_integral_of_sin_over_0_pi():
    assert symbolic.exact_integral("sin(x)", 0.0, math.pi) == pytest.approx(2.0)


def test_exact_integral_of_x_squared():
    assert symbolic.exact_integral("x^2", 0.0, 3.0) == pytest.approx(9.0)


def test_symbolic_rejects_unsafe_expression():
    with pytest.raises(Exception):
        symbolic.exact_derivative("__import__('os')", 1.0)
