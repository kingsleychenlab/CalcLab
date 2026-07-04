"""CalcLab - a lightweight numerical calculus toolkit.

Public helpers are re-exported here so the package can be used as a small
library in addition to its command-line interface::

    >>> from calclab import make_function, differentiate, integrate
    >>> f = make_function("x^2")
    >>> float(round(differentiate(f, 3.0), 4))
    6.0
    >>> float(round(integrate(f, 0, 3, 100, "simpson"), 4))
    9.0
"""

from .functions import make_function, sample, ExpressionError
from .differentiation import (
    differentiate,
    forward_difference,
    backward_difference,
    central_difference,
)
from .integration import (
    integrate,
    left_riemann,
    right_riemann,
    midpoint_riemann,
    trapezoidal,
    simpson,
)
from .errors import absolute_error, relative_error, error_report

__version__ = "0.1.0"

__all__ = [
    "make_function",
    "sample",
    "ExpressionError",
    "differentiate",
    "forward_difference",
    "backward_difference",
    "central_difference",
    "integrate",
    "left_riemann",
    "right_riemann",
    "midpoint_riemann",
    "trapezoidal",
    "simpson",
    "absolute_error",
    "relative_error",
    "error_report",
    "__version__",
]
