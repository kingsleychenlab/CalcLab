import numpy as np
import pytest

from calclab.functions import make_function, sample, ExpressionError


def test_polynomial_evaluation():
    f = make_function("x^2")
    assert f(3) == 9
    assert f(-2) == 4


def test_caret_is_treated_as_power():
    f = make_function("x^3")
    assert f(2) == 8


def test_named_functions():
    assert make_function("sin(x)")(0) == pytest.approx(0.0)
    assert make_function("exp(x)")(1) == pytest.approx(np.e)
    assert make_function("sqrt(x)")(9) == pytest.approx(3.0)


def test_constants_and_compound_expressions():
    assert make_function("cos(pi)")(0) == pytest.approx(-1.0)
    assert make_function("2*x + 1")(3) == pytest.approx(7.0)


def test_vectorised_evaluation_over_array():
    f = make_function("x^2")
    np.testing.assert_allclose(f(np.array([1.0, 2.0, 3.0])), [1.0, 4.0, 9.0])


def test_constant_expression_broadcasts_via_sample():
    f = make_function("5")
    xs = np.linspace(0, 1, 4)
    np.testing.assert_allclose(sample(f, xs), np.full(4, 5.0))


@pytest.mark.parametrize(
    "expr",
    [
        "__import__('os').system('ls')",  # imports
        "x.__class__",                     # attribute access
        "open('secret')",                  # disallowed call
        "unknown(x)",                      # unknown function
        "y + 1",                           # unknown variable
        "2 +",                             # syntax error
        "[1, 2, 3]",                       # list literal
    ],
)
def test_unsafe_or_invalid_expressions_are_rejected(expr):
    with pytest.raises(ExpressionError):
        make_function(expr)
