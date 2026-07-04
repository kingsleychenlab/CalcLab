import math

import pytest

from calclab.errors import absolute_error, relative_error, error_report


def test_absolute_error_is_symmetric_magnitude():
    assert absolute_error(5.0, 3.0) == 2.0
    assert absolute_error(3.0, 5.0) == 2.0


def test_relative_error_basic():
    assert relative_error(5.0, 4.0) == pytest.approx(0.25)


def test_relative_error_with_exact_zero_and_nonzero_approx_is_inf():
    # Undefined mathematically; we return inf rather than crashing.
    assert relative_error(1.0, 0.0) == math.inf


def test_relative_error_with_exact_zero_and_zero_approx_is_zero():
    assert relative_error(0.0, 0.0) == 0.0


def test_error_report_contents():
    report = error_report(2.0, 1.0)
    assert report["approximate"] == 2.0
    assert report["exact"] == 1.0
    assert report["absolute_error"] == 1.0
    assert report["relative_error"] == pytest.approx(1.0)
