"""Growth trajectory simulations — synthesizing all models."""

import numpy as np


def simulate_scenario(
    g_tfp_base: float,
    automation_boost: float,
    automation_speed: float,
    s: float,
    alpha: float,
    delta: float,
    horizon: int,
    compute_growth: float = 0.0,
    scenario: str = "baseline",
) -> dict:
    """Simulate GDP trajectory under different AI scenarios.

    Scenarios:
    - baseline: constant TFP growth
    - moderate: automation boosts TFP with diminishing returns (weak links model)
    - aggressive: compute-driven growth approaching compute growth rate (Restrepo)

    Returns dict with time-series arrays.
    """
    T = horizon
    t = np.arange(T)

    # Initial conditions
    k = np.zeros(T)
    y = np.zeros(T)
    A = np.zeros(T)
    beta = np.zeros(T)  # automation share
    g_t = np.zeros(T)   # growth rate of output

    k[0] = 1.0
    A[0] = 1.0
    beta[0] = 0.1

    for i in range(T):
        if scenario == "baseline":
            if i > 0:
                A[i] = A[i - 1] * (1 + g_tfp_base)
            beta[i] = beta[0]

        elif scenario == "moderate":
            if i > 0:
                # Automation fraction grows logistically
                beta[i] = min(0.95, beta[i - 1] + automation_speed * beta[i - 1] * (1 - beta[i - 1]))
                # TFP boost with diminishing returns (weak link: can't automate everything)
                boost = automation_boost * beta[i] * (1 - beta[i] ** 2)
                A[i] = A[i - 1] * (1 + g_tfp_base + boost)
            else:
                beta[i] = beta[0]

        elif scenario == "aggressive":
            if i > 0:
                # Fast automation
                beta[i] = min(0.99, beta[i - 1] + 2 * automation_speed * beta[i - 1] * (1 - beta[i - 1]))
                # Growth approaches compute growth rate
                effective_g = g_tfp_base + (compute_growth - g_tfp_base) * beta[i]
                A[i] = A[i - 1] * (1 + effective_g)
            else:
                beta[i] = beta[0]

        # Solow dynamics: y = A * k^α, k evolves
        if i > 0:
            k[i] = s * A[i - 1] * k[i - 1] ** alpha + (1 - delta) * k[i - 1]

        y[i] = A[i] * k[i] ** alpha

        if i > 0:
            g_t[i] = (y[i] / y[i - 1]) - 1

    # Labor share: in baseline ~0.65, declines with automation
    if scenario == "baseline":
        labor_share = np.full(T, 1 - alpha)
    elif scenario == "moderate":
        labor_share = (1 - alpha) * (1 - 0.6 * beta)
    else:
        labor_share = (1 - alpha) * (1 - beta)

    return {
        "t": t,
        "y": y,
        "k": k,
        "A": A,
        "beta": beta,
        "g": g_t,
        "labor_share": labor_share,
    }
