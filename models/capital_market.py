"""Capital market supply & demand with CES production."""

import numpy as np
from scipy.optimize import brentq


def ces_output(K: np.ndarray, L: float, a: float, rho: float, A: float = 1.0) -> np.ndarray:
    """CES production: Y = A * (a*K^ρ + (1-a)*L^ρ)^(1/ρ).

    a is capital weight (0 < a < 1), A is TFP.
    Falls back to Cobb-Douglas Y = A * K^a * L^(1-a) when ρ ≈ 0.
    """
    b = 1.0 - a
    if abs(rho) < 1e-8:
        return A * K ** a * L ** b
    return A * (a * K ** rho + b * L ** rho) ** (1.0 / rho)


def mpk(K: np.ndarray, L: float, a: float, rho: float, A: float = 1.0) -> np.ndarray:
    """Marginal product of capital."""
    b = 1.0 - a
    if abs(rho) < 1e-8:
        return A * a * K ** (a - 1) * L ** b
    inner = a * K ** rho + b * L ** rho
    return A * a * K ** (rho - 1) * inner ** (1.0 / rho - 1.0)


def capital_supply(delta: float, impatience: float) -> float:
    """Required return: r = δ + ρ_impatience."""
    return delta + impatience


def _mpk_scalar(K: float, L: float, a: float, rho: float, A: float) -> float:
    """MPK at scalar K."""
    if K <= 0:
        return np.inf
    b = 1.0 - a
    if abs(rho) < 1e-8:
        return A * a * K ** (a - 1) * L ** b
    inner = a * K ** rho + b * L ** rho
    return A * a * K ** (rho - 1) * inner ** (1.0 / rho - 1.0)


def equilibrium_K(L: float, a: float, rho: float, delta: float,
                  impatience: float, A: float = 1.0) -> float:
    """Find equilibrium K where MPK = required return."""
    r_req = capital_supply(delta, impatience)

    def excess(logK):
        K = np.exp(logK)
        return _mpk_scalar(K, L, a, rho, A) - r_req

    lo, hi = -5.0, 50.0
    try:
        e_lo, e_hi = excess(lo), excess(hi)
        if e_lo * e_hi > 0:
            return np.nan
        logK_star = brentq(excess, lo, hi, maxiter=200)
        return np.exp(logK_star)
    except (ValueError, RuntimeWarning, FloatingPointError):
        return np.nan


def capital_share(K: float, L: float, a: float, rho: float, A: float = 1.0) -> float:
    """Capital's share of income: MPK*K / Y."""
    K_arr = np.array([K])
    Y = ces_output(K_arr, L, a, rho, A)[0]
    mk = mpk(K_arr, L, a, rho, A)[0]
    return mk * K / Y


def rho_from_sigma(sigma: float) -> float:
    """ρ = (σ-1)/σ."""
    return (sigma - 1.0) / sigma
