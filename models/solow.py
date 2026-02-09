"""Solow growth model with intermediate goods (Jones 2010)."""

import numpy as np


def production(K: float, L: float, A: float, alpha: float, sigma: float) -> float:
    """Production with intermediate goods: Q = A * (K^α L^(1-α))^(1-σ) * X^σ.

    In steady state, intermediate goods X are produced from final output,
    so we can express per-capita output as a function of capital per worker.
    """
    return A * (K ** alpha * L ** (1 - alpha)) ** (1 - sigma)


def per_capita_production(k: np.ndarray, A: float, alpha: float, sigma: float) -> np.ndarray:
    """Per-capita output y = A * k^(α(1-σ)) — the reduced-form production function."""
    return A * k ** (alpha * (1 - sigma))


def savings_curve(k: np.ndarray, A: float, alpha: float, sigma: float, s: float) -> np.ndarray:
    """Savings per capita: s * y = s * A * k^(α(1-σ))."""
    return s * per_capita_production(k, A, alpha, sigma)


def depreciation_line(k: np.ndarray, delta: float) -> np.ndarray:
    """Break-even investment: δ * k."""
    return delta * k


def steady_state_k(A: float, alpha: float, sigma: float, s: float, delta: float) -> float:
    """Analytical steady state capital per worker.

    From s * A * k^(α(1-σ)) = δ * k:
    k* = (s * A / δ)^(1 / (1 - α(1-σ)))
    """
    exponent = alpha * (1 - sigma)
    return (s * A / delta) ** (1.0 / (1.0 - exponent))


def steady_state_y(A: float, alpha: float, sigma: float, s: float, delta: float) -> float:
    """Steady state output per worker."""
    k_star = steady_state_k(A, alpha, sigma, s, delta)
    return per_capita_production(np.array([k_star]), A, alpha, sigma)[0]


def multiplier(alpha: float, sigma: float) -> float:
    """Development accounting multiplier: 1/((1-α)(1-σ))."""
    return 1.0 / ((1.0 - alpha) * (1.0 - sigma))


def transition_dynamics(A: float, alpha: float, sigma: float, s: float,
                        delta: float, k0: float, T: int) -> tuple[np.ndarray, np.ndarray]:
    """Simulate k_t and y_t over T periods starting from k0.

    k_{t+1} = s * A * k_t^(α(1-σ)) + (1-δ) * k_t
    """
    k = np.zeros(T)
    k[0] = k0
    exp = alpha * (1 - sigma)
    for t in range(T - 1):
        k[t + 1] = s * A * k[t] ** exp + (1 - delta) * k[t]
    y = per_capita_production(k, A, alpha, sigma)
    return k, y


def multiplier_grid(alphas: np.ndarray, sigmas: np.ndarray) -> np.ndarray:
    """Compute multiplier for a grid of (α, σ) values."""
    aa, ss = np.meshgrid(alphas, sigmas)
    return 1.0 / ((1.0 - aa) * (1.0 - ss))


def income_ratio(tfp_ratio: float, alpha: float, sigma: float) -> float:
    """Income ratio given a TFP ratio, using the multiplier.

    If country B has tfp_ratio times the TFP of country A,
    the income ratio is tfp_ratio^multiplier.
    """
    m = multiplier(alpha, sigma)
    return tfp_ratio ** m
