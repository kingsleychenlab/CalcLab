import numpy as np
import pytest

from calclab.differentiation import (
    differentiate,
    forward_difference,
    backward_difference,
    central_difference,
)
from calclab.functions import make_function


def test_derivative_of_x_squared_at_3_is_6():
    f = make_function("x^2")
    for method in ("forward", "backward", "central"):
        assert differentiate(f, 3.0, 1e-5, method) == pytest.approx(6.0, abs=1e-3)


def test_derivative_of_x_cubed_at_2_is_12():
    f = make_function("x^3")
    assert differentiate(f, 2.0, 1e-5, "central") == pytest.approx(12.0, abs=1e-4)


def test_derivative_of_sin_at_0_is_1():
    f = make_function("sin(x)")
    assert differentiate(f, 0.0, 1e-5, "central") == pytest.approx(1.0, abs=1e-6)


def test_central_is_more_accurate_than_forward():
    # For a smooth function the central rule (O(h^2)) should beat the
    # forward rule (O(h)) at the same step size.
    f = make_function("sin(x)")
    x0, h = 1.0, 0.1
    exact = np.cos(1.0)
    err_forward = abs(forward_difference(f, x0, h) - exact)
    err_central = abs(central_difference(f, x0, h) - exact)
    assert err_central < err_forward


def test_backward_difference_matches_formula():
    f = make_function("x^2")
    h = 1e-4
    expected = (f(3.0) - f(3.0 - h)) / h
    assert backward_difference(f, 3.0, h) == pytest.approx(expected)


def test_unknown_method_raises():
    f = make_function("x")
    with pytest.raises(ValueError):
        differentiate(f, 1.0, 1e-5, "nope")


def test_nonpositive_step_raises():
    f = make_function("x")
    with pytest.raises(ValueError):
        differentiate(f, 1.0, 0.0, "central")
