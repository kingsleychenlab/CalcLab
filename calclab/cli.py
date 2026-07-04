"""Command-line interface for CalcLab.

Two subcommands are exposed::

    python -m calclab derivative --function "x^2" --x 3 --h 0.001 --method central
    python -m calclab integrate  --function "x^2" --a 0 --b 3 --n 100 --method trapezoid
"""

import argparse
import sys

from . import differentiation, errors, functions, integration


def build_parser():
    parser = argparse.ArgumentParser(
        prog="calclab",
        description="CalcLab - a tiny numerical calculus toolkit "
                    "(derivatives, integrals, error analysis, plots).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- derivative --------------------------------------------------------
    d = subparsers.add_parser("derivative", help="Estimate f'(x) numerically.")
    d.add_argument("--function", required=True,
                   help='Expression in x, e.g. "x^2" or "sin(x)".')
    d.add_argument("--x", type=float, required=True,
                   help="Point at which to differentiate.")
    d.add_argument("--h", type=float, default=1e-5,
                   help="Step size (default: 1e-5).")
    d.add_argument("--method", choices=sorted(differentiation.METHODS),
                   default="central", help="Finite-difference method (default: central).")
    d.add_argument("--exact", type=float, default=None,
                   help="Known exact value for error comparison.")
    d.add_argument("--symbolic", action="store_true",
                   help="Derive the exact value symbolically with SymPy (optional).")
    d.add_argument("--plot", action="store_true", help="Display a plot.")
    d.add_argument("--save", default=None, metavar="PATH",
                   help="Save the plot to PATH instead of (or as well as) showing it.")

    # ---- integrate ---------------------------------------------------------
    i = subparsers.add_parser("integrate", help="Estimate a definite integral numerically.")
    i.add_argument("--function", required=True,
                   help='Expression in x, e.g. "x^2" or "sin(x)".')
    i.add_argument("--a", type=float, required=True, help="Lower limit of integration.")
    i.add_argument("--b", type=float, required=True, help="Upper limit of integration.")
    i.add_argument("--n", type=int, default=100,
                   help="Number of subintervals (default: 100).")
    i.add_argument("--method", choices=sorted(integration.METHODS),
                   default="trapezoid", help="Quadrature rule (default: trapezoid).")
    i.add_argument("--exact", type=float, default=None,
                   help="Known exact value for error comparison.")
    i.add_argument("--symbolic", action="store_true",
                   help="Integrate exactly with SymPy for comparison (optional).")
    i.add_argument("--plot", action="store_true", help="Display a plot.")
    i.add_argument("--save", default=None, metavar="PATH",
                   help="Save the plot to PATH instead of (or as well as) showing it.")

    return parser


def _fmt(value):
    return f"{float(value):.10g}"


def _print_errors(approx, exact):
    report = errors.error_report(approx, exact)
    print(f"  exact value    = {_fmt(exact)}")
    print(f"  absolute error = {report['absolute_error']:.3e}")
    print(f"  relative error = {report['relative_error']:.3e}")


def _resolve_exact(args, kind):
    """Return an exact value from --symbolic (preferred) or --exact, else None."""
    if args.symbolic:
        from . import symbolic
        try:
            if kind == "derivative":
                return symbolic.exact_derivative(args.function, args.x)
            return symbolic.exact_integral(args.function, args.a, args.b)
        except symbolic.SymbolicUnavailable as exc:
            print(f"  [symbolic] {exc}")
        except Exception as exc:  # SymPy could not parse / integrate the input
            print(f"  [symbolic] could not compute exact value: {exc}")
    return args.exact


def _run_derivative(args):
    f = functions.make_function(args.function)
    approx = differentiation.differentiate(f, args.x, args.h, args.method)

    print("CalcLab :: numerical derivative")
    print(f"  f(x)           = {args.function}")
    print(f"  method         = {args.method} difference")
    print(f"  x, h           = {_fmt(args.x)}, {_fmt(args.h)}")
    print(f"  approximate f' = {_fmt(approx)}")

    exact = _resolve_exact(args, "derivative")
    if exact is not None:
        _print_errors(approx, exact)

    if args.plot or args.save:
        from . import plotting
        plotting.plot_derivative(
            f, args.x, args.h, args.method,
            label=args.function, show=args.plot, save=args.save,
        )


def _run_integrate(args):
    f = functions.make_function(args.function)
    approx = integration.integrate(f, args.a, args.b, args.n, args.method)

    print("CalcLab :: numerical integration")
    print(f"  f(x)            = {args.function}")
    print(f"  method          = {args.method}")
    print(f"  interval, n     = [{_fmt(args.a)}, {_fmt(args.b)}], {args.n}")
    print(f"  approximate int = {_fmt(approx)}")

    exact = _resolve_exact(args, "integral")
    if exact is not None:
        _print_errors(approx, exact)

    if args.plot or args.save:
        from . import plotting
        plotting.plot_integration(
            f, args.a, args.b, args.n, args.method,
            label=args.function, show=args.plot, save=args.save,
        )


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "derivative":
            _run_derivative(args)
        elif args.command == "integrate":
            _run_integrate(args)
    except (functions.ExpressionError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
