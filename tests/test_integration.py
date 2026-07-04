import numpy as np
import pytest

from calclab.integration import (
    integrate,
    left_riemann,
    right_riemann,
    midpoint_riemann,
    trapezoidal,
    simpson,
)
from calclab.functions import make_function

ALL_METHODS = ("left", "right", "midpoint", "trapezoid", "simpson")


def test_integral_of_x_from_0_to_1_is_half():
    f = make_function("x")
    for method in ALL_METHODS:
        assert integrate(f, 0.0, 1.0, 100, method) == pytest.approx(0.5, abs=1e-2)


def test_integral_of_x_squared_from_0_to_3_is_9():
    f = make_function("x^2")
    assert integrate(f, 0.0, 3.0, 100, "trapezoid") == pytest.approx(9.0, abs=1e-2)


def test_integral_of_sin_from_0_to_pi_is_2():
    f = make_function("sin(x)")
    assert integrate(f, 0.0, np.pi, 100, "simpson") == pytest.approx(2.0, abs=1e-6)


def test_simpson_is_exact_for_quadratics():
    f = make_function("x^2")
    # Only floating-point round-off should remain.
    assert simpson(f, 0.0, 3.0, 100) == pytest.approx(9.0, abs=1e-10)


def test_simpson_is_exact_for_cubics():
    f = make_function("x^3")
    # integral of x^3 over [0, 2] = 4 exactly.
    assert simpson(f, 0.0, 2.0, 10) == pytest.approx(4.0, abs=1e-10)


def test_simpson_rejects_odd_n():
    f = make_function("x^2")
    with pytest.raises(ValueError):
        simpson(f, 0.0, 1.0, 7)


def test_midpoint_and_trapezoid_bracket_a_convex_integral():
    # For a convex function the midpoint rule under-estimates and the
    # trapezoidal rule over-estimates the true value.
    f = make_function("x^2")
    exact = 9.0
    assert midpoint_riemann(f, 0.0, 3.0, 50) < exact < trapezoidal(f, 0.0, 3.0, 50)


def test_left_and_right_bracket_an_increasing_integral():
    f = make_function("x^2")
    exact = 9.0
    assert left_riemann(f, 0.0, 3.0, 100) < exact < right_riemann(f, 0.0, 3.0, 100)


def test_more_subintervals_reduce_error():
    f = make_function("sin(x)")
    exact = 2.0
    coarse = abs(trapezoidal(f, 0.0, np.pi, 10) - exact)
    fine = abs(trapezoidal(f, 0.0, np.pi, 200) - exact)
    assert fine < coarse


def test_zero_or_negative_n_raises():
    f = make_function("x")
    with pytest.raises(ValueError):
        integrate(f, 0.0, 1.0, 0, "trapezoid")


def test_unknown_method_raises():
    f = make_function("x")
    with pytest.raises(ValueError):
        integrate(f, 0.0, 1.0, 10, "nope")
