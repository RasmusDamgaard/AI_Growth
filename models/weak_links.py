"""Weak links and task automation model (Jones & Tonetti)."""

import numpy as np


def ces_aggregate(task_outputs: np.ndarray, sigma: float,
                  weights: np.ndarray | None = None) -> float:
    """CES aggregation of task outputs.

    Y = (Σ α_i Y_i^((σ-1)/σ))^(σ/(σ-1))
    """
    n = len(task_outputs)
    if weights is None:
        weights = np.ones(n) / n

    rho = (sigma - 1.0) / sigma
    if abs(rho) < 1e-10:
        # Cobb-Douglas limit
        return np.prod(task_outputs ** weights)

    inner = np.sum(weights * task_outputs ** rho)
    if inner <= 0:
        return 0.0
    return inner ** (1.0 / rho)


def task_output(psi_k: float, K_i: float, psi_l: float, L_i: float) -> float:
    """Task production: Y_i = ψ_ki * K_i + ψ_li * L_i."""
    return psi_k * K_i + psi_l * L_i


def simulate_automation(n: int, sigma: float, g_k: float, g_l: float,
                        beta_0: float, years: int,
                        K_total: float = 10.0, L_total: float = 10.0,
                        Z: float = 1.0) -> dict:
    """Simulate task automation over time.

    Capital productivity grows at g_k, labor at g_l.
    Tasks switch from labor to capital when capital becomes more productive.

    Returns dict with time series arrays.
    """
    T = years
    t_arr = np.arange(T)

    # Productivity paths
    psi_k_base = 1.0
    psi_l_base = 1.0
    psi_k_t = psi_k_base * (1 + g_k) ** t_arr
    psi_l_t = psi_l_base * (1 + g_l) ** t_arr

    # Track outputs
    gdp = np.zeros(T)
    gdp_baseline = np.zeros(T)
    gdp_full_auto = np.zeros(T)
    beta_t = np.zeros(T)
    capital_share = np.zeros(T)

    for t in range(T):
        # Endogenous automation: tasks use capital if psi_k > psi_l
        # Start with beta_0 fraction automated, expand as capital gets better
        ratio = psi_k_t[t] / psi_l_t[t]
        # Fraction automated grows with relative capital productivity
        beta = min(1.0, beta_0 + (1 - beta_0) * (1 - 1.0 / max(ratio, 1.0)))
        beta_t[t] = beta

        n_auto = int(round(beta * n))
        n_manual = n - n_auto

        # Allocate resources
        task_outputs = np.zeros(n)
        k_income = 0.0
        total_income = 0.0

        for i in range(n):
            if i < n_auto:
                # Capital-based task
                K_i = K_total / max(n_auto, 1)
                out = psi_k_t[t] * K_i
                k_income += out
            else:
                # Labor-based task
                L_i = L_total / max(n_manual, 1)
                out = psi_l_t[t] * L_i
            task_outputs[i] = out
            total_income += out

        gdp[t] = Z * ces_aggregate(task_outputs, sigma)
        capital_share[t] = k_income / total_income if total_income > 0 else 0

        # Baseline: no automation growth (fixed beta_0)
        n_auto_base = int(round(beta_0 * n))
        n_manual_base = n - n_auto_base
        base_outputs = np.zeros(n)
        for i in range(n):
            if i < n_auto_base:
                K_i = K_total / max(n_auto_base, 1)
                base_outputs[i] = psi_k_t[t] * K_i
            else:
                L_i = L_total / max(n_manual_base, 1)
                base_outputs[i] = psi_l_t[t] * L_i
        gdp_baseline[t] = Z * ces_aggregate(base_outputs, sigma)

        # Full automation
        full_outputs = np.full(n, psi_k_t[t] * K_total / n)
        gdp_full_auto[t] = Z * ces_aggregate(full_outputs, sigma)

    return {
        "t": t_arr,
        "gdp": gdp,
        "gdp_baseline": gdp_baseline,
        "gdp_full_auto": gdp_full_auto,
        "beta": beta_t,
        "capital_share": capital_share,
        "psi_k": psi_k_t,
        "psi_l": psi_l_t,
    }


def weak_link_demo(n: int, sigma_low: float, sigma_high: float) -> dict:
    """Demonstrate weak link effect: one low-quality task constrains output when σ<1."""
    task_outputs_uniform = np.ones(n) * 5.0
    task_outputs_weak = np.ones(n) * 5.0
    task_outputs_weak[n // 2] = 1.0  # One weak task

    y_uniform_low = ces_aggregate(task_outputs_uniform, sigma_low)
    y_weak_low = ces_aggregate(task_outputs_weak, sigma_low)
    y_uniform_high = ces_aggregate(task_outputs_uniform, sigma_high)
    y_weak_high = ces_aggregate(task_outputs_weak, sigma_high)

    return {
        "task_outputs_uniform": task_outputs_uniform,
        "task_outputs_weak": task_outputs_weak,
        "y_uniform_low": y_uniform_low,
        "y_weak_low": y_weak_low,
        "y_uniform_high": y_uniform_high,
        "y_weak_high": y_weak_high,
    }
