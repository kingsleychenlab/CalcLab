"""Safe parsing of mathematical expressions into callable functions.

Expressions such as ``"x^2"`` or ``"sin(x)"`` are turned into Python callables
without ever calling :func:`eval`.  We parse the text with the :mod:`ast`
module and then walk the resulting tree against a strict allow-list of nodes,
names and functions.  Anything outside that list (attribute access, imports,
arbitrary calls, ...) is rejected before a single value is ever computed.
"""

import ast
import operator

import numpy as np

# Functions the user may call, mapped to their vectorised NumPy implementation.
ALLOWED_FUNCTIONS = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "asin": np.arcsin,
    "acos": np.arccos,
    "atan": np.arctan,
    "sinh": np.sinh,
    "cosh": np.cosh,
    "tanh": np.tanh,
    "exp": np.exp,
    "log": np.log,      # natural logarithm
    "log10": np.log10,
    "log2": np.log2,
    "sqrt": np.sqrt,
    "abs": np.abs,
}

# Bare names that resolve to numeric constants.
ALLOWED_CONSTANTS = {
    "pi": np.pi,
    "e": np.e,
    "tau": 2.0 * np.pi,
}

# Binary and unary operators we accept, mapped to the matching Python operator.
_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}

_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

# Every AST node type that is allowed to appear in a valid expression.
_ALLOWED_NODES = (
    ast.Expression,
    ast.BinOp,
    ast.UnaryOp,
    ast.Call,
    ast.Name,
    ast.Load,
    ast.Constant,
) + tuple(_BINARY_OPS) + tuple(_UNARY_OPS)


class ExpressionError(ValueError):
    """Raised when an expression is malformed or uses disallowed features."""


def make_function(expression):
    """Compile ``expression`` into a safe callable ``f(x)``.

    ``x`` is the independent variable.  The returned callable accepts plain
    Python numbers as well as NumPy arrays, so the same object can be used for
    pointwise differentiation and for vectorised integration/plotting.
    """
    # In everyday maths ``^`` means exponentiation; in Python that is ``**``.
    normalised = expression.replace("^", "**")
    try:
        tree = ast.parse(normalised, mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(
            f"Could not parse expression {expression!r}: {exc.msg}."
        ) from exc

    _validate(tree)

    def f(x):
        return _evaluate(tree.body, x)

    f.expression = expression
    return f


def sample(f, xs):
    """Evaluate ``f`` across the array ``xs``, broadcasting constant results.

    A constant expression such as ``"5"`` ignores its argument and returns a
    scalar.  Broadcasting guarantees the output always matches the input shape,
    so the integration and plotting routines can rely on element-wise arrays.
    """
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(f(xs), dtype=float)
    if ys.shape != xs.shape:
        ys = np.broadcast_to(ys, xs.shape)
    return ys


def _validate(tree):
    """Walk the tree once and reject anything outside the allow-list."""
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise ExpressionError(f"Disallowed syntax: {type(node).__name__}.")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ExpressionError("Only direct calls to allowed functions are permitted.")
            if node.func.id not in ALLOWED_FUNCTIONS:
                raise ExpressionError(f"Function {node.func.id!r} is not allowed.")
            if node.keywords:
                raise ExpressionError("Keyword arguments are not allowed.")

        elif isinstance(node, ast.Name):
            known = {"x"} | set(ALLOWED_CONSTANTS) | set(ALLOWED_FUNCTIONS)
            if node.id not in known:
                raise ExpressionError(f"Unknown name {node.id!r}.")

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
                raise ExpressionError("Only numeric constants are allowed.")


def _evaluate(node, x):
    """Recursively evaluate a validated AST node at point(s) ``x``."""
    if isinstance(node, ast.BinOp):
        left = _evaluate(node.left, x)
        right = _evaluate(node.right, x)
        return _BINARY_OPS[type(node.op)](left, right)

    if isinstance(node, ast.UnaryOp):
        return _UNARY_OPS[type(node.op)](_evaluate(node.operand, x))

    if isinstance(node, ast.Call):
        args = [_evaluate(arg, x) for arg in node.args]
        return ALLOWED_FUNCTIONS[node.func.id](*args)

    if isinstance(node, ast.Name):
        if node.id == "x":
            return x
        return ALLOWED_CONSTANTS[node.id]

    if isinstance(node, ast.Constant):
        return node.value

    # Unreachable once _validate has run, but kept as a defensive guard.
    raise ExpressionError(f"Cannot evaluate node {type(node).__name__}.")
