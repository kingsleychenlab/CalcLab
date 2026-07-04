# CalcLab

A lightweight Python command-line toolkit for **numerical calculus**: finite-difference
derivatives, numerical integration (quadrature), error analysis against exact values, and
simple Matplotlib visualizations.

Every method is implemented **by hand from its mathematical definition** — no
`scipy.integrate`, no `scipy.misc`, no hidden shortcuts. NumPy is used only for arrays and
vectorized arithmetic, Matplotlib only for plotting, and SymPy only (and optionally) to
compute exact values for comparison. The point of CalcLab is to *prove the math works* through
runnable examples, plots, and tests.

```bash
python -m calclab derivative --function "x^2" --x 3 --h 0.001 --method central
python -m calclab integrate  --function "x^2" --a 0 --b 3 --n 100 --method trapezoid
python -m calclab integrate  --function "sin(x)" --a 0 --b 3.14159 --n 100 --method simpson --exact 2 --plot
```

---

## Why numerical calculus matters

Most functions you meet in the real world — sensor readings, simulation outputs, messy
data-driven models — have **no closed-form derivative or integral**. Even when a symbolic
answer exists, it may be too expensive or unstable to evaluate. Numerical calculus lets you:

- differentiate a function you can only *sample* (finite differences),
- integrate a function whose antiderivative is unknown (e.g. `sin(x)/x`, `exp(-x^2)`),
- trade a little accuracy for a lot of speed, in a controlled way.

The catch is that every numerical method carries **error** that depends on the step size and
the method's order. CalcLab makes that trade-off visible: it reports absolute and relative
error, and shows how central differences (error `O(h^2)`) beat forward differences (error
`O(h)`), and how Simpson's rule is *exact* for polynomials up to degree three.

---

## Formulas used

### Derivatives (step size `h`)

| Method    | Formula                                | Error   |
|-----------|----------------------------------------|---------|
| Forward   | `f'(x) ≈ [f(x + h) − f(x)] / h`        | `O(h)`  |
| Backward  | `f'(x) ≈ [f(x) − f(x − h)] / h`        | `O(h)`  |
| Central   | `f'(x) ≈ [f(x + h) − f(x − h)] / (2h)` | `O(h²)` |

### Integrals (interval `[a, b]`, `n` subintervals, `Δx = (b − a)/n`)

| Method       | Formula                                                              |
|--------------|---------------------------------------------------------------------|
| Left Riemann | `Δx · Σ f(xᵢ)` sampled at the left endpoints                        |
| Right Riemann| `Δx · Σ f(xᵢ)` sampled at the right endpoints                       |
| Midpoint     | `Δx · Σ f((xᵢ + xᵢ₊₁)/2)`                                           |
| Trapezoidal  | `(Δx/2) · [f(x₀) + 2 Σ f(xᵢ) + f(xₙ)]`                              |
| Simpson      | `(Δx/3) · [f(x₀) + 4 Σ f(x_odd) + 2 Σ f(x_even) + f(xₙ)]` (`n` even)|

**Simpson's rule requires an even number of subintervals `n`.** An odd `n` raises a clear error.

### Error comparison

```
absolute error = |approximate − exact|
relative error = |approximate − exact| / |exact|     (0 if both are 0, ∞ if only exact is 0)
```

---

## Setup

Requires Python 3.8+.

```bash
git clone <your-fork-url> CalcLab
cd CalcLab

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt  # numpy, matplotlib, pytest
# optional, for --symbolic exact comparison:
pip install sympy
```

Run the tests to confirm everything works from a fresh clone:

```bash
pytest
```

---

## CLI usage

```
python -m calclab derivative --function EXPR --x X [--h H] [--method M] [--exact E] [--symbolic] [--plot] [--save PATH]
python -m calclab integrate  --function EXPR --a A --b B [--n N] [--method M] [--exact E] [--symbolic] [--plot] [--save PATH]
```

- `--method` for `derivative`: `forward`, `backward`, `central` (default `central`)
- `--method` for `integrate`: `left`, `right`, `midpoint`, `trapezoid`, `simpson` (default `trapezoid`)
- `--exact` supplies a known true value so CalcLab can report the error
- `--symbolic` computes the exact value automatically with SymPy (optional dependency)
- `--plot` shows a figure; `--save PATH` writes it to a PNG

### Supported expressions

Expressions are parsed with a **safe AST evaluator** (never `eval`). Multiplication must be
explicit (`2*x`, not `2x`), and `^` is treated as exponentiation.

- polynomials: `x`, `x^2`, `x^3`, `2*x + 1`, ...
- trig: `sin(x)`, `cos(x)`, `tan(x)` (plus `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`)
- `exp(x)`, `log(x)` (natural log), `log10(x)`, `log2(x)`, `sqrt(x)`, `abs(x)`
- constants: `pi`, `e`, `tau`

Anything else — attribute access, imports, unknown names/functions — is rejected:

```
$ python -m calclab derivative --function "__import__('os').system('ls')" --x 1
Error: Only direct calls to allowed functions are permitted.
```

---

## Sample outputs

**Derivative with automatic (symbolic) exact comparison:**

```
$ python -m calclab derivative --function "sin(x)" --x 1 --method central --symbolic
CalcLab :: numerical derivative
  f(x)           = sin(x)
  method         = central difference
  x, h           = 1, 1e-05
  approximate f' = 0.5403023059
  exact value    = 0.5403023059
  absolute error = 1.114e-11
  relative error = 2.062e-11
```

**Integration, Simpson's rule vs a known exact value:**

```
$ python -m calclab integrate --function "sin(x)" --a 0 --b 3.14159 --n 100 --method simpson --exact 2
CalcLab :: numerical integration
  f(x)            = sin(x)
  method          = simpson
  interval, n     = [0, 3.14159], 100
  approximate int = 2.000000011
  exact value    = 2
  absolute error = 1.082e-08
  relative error = 5.410e-09
```

**The methods, side by side** — `d/dx x²` at `x = 3` with a deliberately large `h = 0.1`
(exact answer `6`). Central difference is *exact* here because `x²` has zero third derivative:

| Method    | Approximation | Absolute error |
|-----------|---------------|----------------|
| Forward   | `6.1`         | `1.0e-01`      |
| Backward  | `5.9`         | `1.0e-01`      |
| Central   | `6.0`         | `5.3e-15`      |

And `∫₀³ x² dx` (exact `9`) with only `n = 10` subintervals:

| Method       | Approximation | Absolute error |
|--------------|---------------|----------------|
| Left Riemann | `7.695`       | `1.31e+00`     |
| Right Riemann| `10.395`      | `1.40e+00`     |
| Midpoint     | `8.9775`      | `2.25e-02`     |
| Trapezoid    | `9.045`       | `4.50e-02`     |
| Simpson      | `9.0`         | `1.78e-15`     |

Simpson's rule nails a quadratic to machine precision with just 10 subintervals.

---

## Plot examples

Generated with `--save` (`python -m calclab ... --save examples/images/<name>.png`):

**Derivative — tangent line** (`derivative --function "x^2" --x 3 --method central`):

![Derivative tangent line](examples/images/derivative_x2.png)

**Midpoint rule — rectangles** (`integrate --function "x^2" --a 0 --b 3 --n 12 --method midpoint`):

![Midpoint rectangles](examples/images/midpoint_x2.png)

**Trapezoidal rule — trapezoids** (`integrate --function "sin(x)" --a 0 --b 3.14159 --n 10 --method trapezoid`):

![Trapezoids](examples/images/trapezoid_sin.png)

**Simpson's rule — shaded area** (`integrate --function "sin(x)" --a 0 --b 3.14159 --n 100 --method simpson`):

![Simpson area](examples/images/simpson_sin.png)

---

## Project layout

```
CalcLab/
├── README.md
├── requirements.txt
├── conftest.py                 # puts the repo root on sys.path for pytest
├── calclab/
│   ├── __init__.py             # public API re-exports
│   ├── __main__.py             # enables `python -m calclab`
│   ├── cli.py                  # argparse CLI
│   ├── functions.py            # safe expression parser (AST, no eval)
│   ├── differentiation.py      # forward / backward / central
│   ├── integration.py          # left / right / midpoint / trapezoid / simpson
│   ├── errors.py               # absolute / relative error
│   ├── plotting.py             # Matplotlib visualizations (lazy import)
│   └── symbolic.py             # optional SymPy exact comparison
├── tests/
│   ├── test_functions.py
│   ├── test_differentiation.py
│   ├── test_integration.py
│   ├── test_errors.py
│   └── test_symbolic.py        # skipped if SymPy is absent
└── examples/
    ├── sample_usage.md
    └── images/                 # generated plots
```

You can also use CalcLab as a tiny library:

```python
from calclab import make_function, differentiate, integrate

f = make_function("x^2")
differentiate(f, 3.0, method="central")   # ≈ 6.0
integrate(f, 0, 3, n=100, method="simpson")  # ≈ 9.0
```

---

## Limitations

- **Single variable only.** Expressions are functions of one variable, `x`.
- **Uniform grids.** Integration uses equally spaced nodes; there is no adaptive refinement.
- **Naive step size.** Very small `h` in differentiation eventually loses accuracy to
  floating-point round-off (subtractive cancellation); the default `1e-5` is a safe middle ground.
- **No complex numbers, no discontinuity handling.** Sampling a point outside a function's
  domain (e.g. `log(x)` at `x ≤ 0`) yields `nan`, as NumPy would.
- **Plots are illustrative,** not publication-grade; for large `n` the individual
  rectangle/trapezoid edges are hidden to keep the figure readable.

## Future improvements

- Higher-order differences (five-point stencil) and Richardson extrapolation.
- Adaptive quadrature and Gaussian quadrature.
- Convergence plots: error vs `n` (or `h`) on a log-log scale to visualize method order.
- A `compare` subcommand that runs every method at once and tabulates the errors.
- Optional Romberg integration.

---

## License

MIT — do whatever you like; attribution appreciated.
