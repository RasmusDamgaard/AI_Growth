"""O-Ring production and focus effect (Gans & Goldfarb)."""

import numpy as np


def oring_output_manual(n: int, a: float, h: float) -> float:
    """Output when all tasks done manually: Y = (ah/n)^n."""
    q = a * h / n
    return q ** n


def oring_output_automated(k: int, n: int, a: float, h: float, theta: float) -> float:
    """Output with k tasks automated, (n-k) done manually.

    Y(k) = θ^k * (ah/(n-k))^(n-k)
    Workers concentrate time on fewer tasks → quality rises (focus effect).
    """
    if k >= n:
        return theta ** n
    manual = n - k
    q_manual = a * h / manual
    return (theta ** k) * (q_manual ** manual)


def net_surplus(k: int, n: int, a: float, h: float, theta: float, r: float) -> float:
    """Net output after capital cost: S(k) = Y(k) - r*k."""
    return oring_output_automated(k, n, a, h, theta) - r * k


def optimal_k(n: int, a: float, h: float, theta: float, r: float) -> int:
    """Find the profit-maximizing number of automated tasks."""
    best_k = 0
    best_s = net_surplus(0, n, a, h, theta, r)
    for k in range(n + 1):
        s = net_surplus(k, n, a, h, theta, r)
        if s > best_s:
            best_s = s
            best_k = k
    return best_k


def optimal_manual_tasks(a: float, h: float, theta: float) -> float:
    """Optimal number of remaining manual tasks: m* = ah/(θe)."""
    return a * h / (theta * np.e)


def rising_threshold(m: np.ndarray, a: float, h: float) -> np.ndarray:
    """Minimum machine quality to automate down to m manual tasks.

    θ̄(m) = (ah/m) * ((m-1)/m)^(m-1)
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        result = (a * h / m) * ((m - 1) / m) ** (m - 1)
        result = np.where(m < 1, np.nan, result)
    return result


def wage_under_automation(k: int, n: int, a: float, h: float, theta: float,
                          beta: float) -> float:
    """Worker wage with k automated tasks (Nash bargaining).

    W(k) = β * Y(k)
    """
    return beta * oring_output_automated(k, n, a, h, theta)


def profit_under_automation(k: int, n: int, a: float, h: float, theta: float,
                            r: float, beta: float) -> float:
    """Firm profit: Π(k) = (1-β)*Y(k) - r*k."""
    y = oring_output_automated(k, n, a, h, theta)
    return (1 - beta) * y - r * k


def output_curve(n: int, a: float, h: float, theta: float) -> tuple[np.ndarray, np.ndarray]:
    """Compute Y(k) for k = 0, 1, ..., n."""
    ks = np.arange(n + 1)
    ys = np.array([oring_output_automated(int(k), n, a, h, theta) for k in ks])
    return ks, ys


def time_allocation(k: int, n: int, h: float) -> tuple[np.ndarray, np.ndarray]:
    """Time per task before and after automation.

    Before: h/n each. After: 0 for automated, h/(n-k) for manual.
    """
    before = np.full(n, h / n)
    after = np.zeros(n)
    manual = n - k
    if manual > 0:
        after[k:] = h / manual
    return before, after
