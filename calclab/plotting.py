"""Matplotlib visualisations for derivatives and integrals.

Plotting is intentionally optional and lazily imported: the numerical core
never imports Matplotlib, so CalcLab (and its tests) still run in a headless
environment.  The pictures are meant to make the maths obvious - a tangent line
for a derivative, and the sampled rectangles/trapezoids for an integral - not
to be publication-grade figures.
"""

import os

import numpy as np

from . import differentiation, integration
from .functions import sample


def _lazy_pyplot():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise RuntimeError(
            "Matplotlib is required for plotting. Install it with "
            "'pip install matplotlib'."
        ) from exc
    return plt


def _finish(plt, fig, show, save):
    if save:
        directory = os.path.dirname(save)
        if directory:
            os.makedirs(directory, exist_ok=True)
        fig.savefig(save, dpi=120, bbox_inches="tight")
        print(f"Saved plot to {save}")
    if show:
        plt.show()
    plt.close(fig)


def plot_derivative(f, x0, h=1e-5, method="central", label="f(x)", show=True, save=None):
    """Plot ``f`` around ``x0`` together with the numerical tangent line."""
    plt = _lazy_pyplot()
    slope = differentiation.differentiate(f, x0, h, method)
    y0 = float(f(x0))

    half_width = 2.0
    xs = np.linspace(x0 - half_width, x0 + half_width, 400)
    ys = sample(f, xs)
    tangent = y0 + slope * (xs - x0)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(xs, ys, color="C0", linewidth=2, label=f"f(x) = {label}")
    ax.plot(xs, tangent, "--", color="C3", label=f"tangent (slope ~= {slope:.4f})")
    ax.plot([x0], [y0], "o", color="C3", zorder=5)
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.axvline(0, color="grey", linewidth=0.8)
    ax.set_title(f"{method.capitalize()} difference derivative at x = {x0}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    ax.grid(True, alpha=0.3)
    _finish(plt, fig, show, save)


def plot_integration(f, a, b, n=100, method="trapezoid", label="f(x)", show=True, save=None):
    """Plot ``f`` over ``[a, b]`` with the geometry of the chosen rule."""
    plt = _lazy_pyplot()
    approx = integration.integrate(f, a, b, n, method)

    xs = np.linspace(a, b, 400)
    ys = sample(f, xs)

    fig, ax = plt.subplots(figsize=(7, 5))

    if method in ("left", "right", "midpoint"):
        _draw_rectangles(ax, f, a, b, n, method)
    elif method == "trapezoid":
        _draw_trapezoids(ax, f, a, b, n)
    else:  # simpson (or any area-only view): shade under the curve
        ax.fill_between(xs, ys, alpha=0.25, color="C1", label="area")

    ax.plot(xs, ys, color="C0", linewidth=2, label=f"f(x) = {label}", zorder=5)
    ax.axhline(0, color="grey", linewidth=0.8)
    ax.set_title(f"{method.capitalize()} rule:  integral ~= {approx:.6f}   (n = {n})")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    ax.grid(True, alpha=0.3)
    _finish(plt, fig, show, save)


def _draw_rectangles(ax, f, a, b, n, method):
    edges = np.linspace(a, b, n + 1)
    dx = (b - a) / n
    if method == "left":
        sample_x = edges[:-1]
    elif method == "right":
        sample_x = edges[1:]
    else:  # midpoint
        sample_x = (edges[:-1] + edges[1:]) / 2.0
    heights = sample(f, sample_x)
    # Hide the individual edges once there are too many to read.
    edgecolor = "C0" if n <= 40 else "none"
    ax.bar(
        edges[:-1], heights, width=dx, align="edge",
        alpha=0.35, color="C1", edgecolor=edgecolor, linewidth=0.6,
        label=f"{n} rectangles",
    )


def _draw_trapezoids(ax, f, a, b, n):
    edges = np.linspace(a, b, n + 1)
    ys = sample(f, edges)
    edgecolor = "C0" if n <= 40 else "none"
    for i in range(n):
        ax.fill(
            [edges[i], edges[i], edges[i + 1], edges[i + 1]],
            [0, ys[i], ys[i + 1], 0],
            color="C1", alpha=0.35, edgecolor=edgecolor, linewidth=0.6,
        )
    ax.plot([], [], color="C1", alpha=0.5, linewidth=8, label=f"{n} trapezoids")
