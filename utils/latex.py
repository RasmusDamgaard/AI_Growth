# Pre-formatted LaTeX equation strings for display with st.latex()

# --- Solow Model ---
SOLOW_PRODUCTION = r"Q = A \left( K^{\alpha} L^{1-\alpha} \right)^{1-\sigma} X^{\sigma}"
SOLOW_STEADY_STATE = r"y^* = \left( A \cdot m \left( \frac{s}{\delta} \right)^{\alpha(1-\sigma)} \right)^{\frac{1}{(1-\alpha)(1-\sigma)}}"
SOLOW_MULTIPLIER = r"\text{Multiplier} = \frac{1}{(1-\alpha)(1-\sigma)}"
SOLOW_TRANSITION = r"k_{t+1} = s \cdot A \cdot k_t^{\alpha} + (1-\delta) k_t"

# --- Weak Links ---
CES_AGGREGATION = r"Y = Z \left( \sum_{i=1}^{n} \alpha_i Y_i^{\frac{\sigma-1}{\sigma}} \right)^{\frac{\sigma}{\sigma-1}}"
TASK_PRODUCTION = r"Y_i = \psi_{ki} K_i + \psi_{li} L_i"

# --- O-Ring ---
ORING_PRODUCTION = r"Y = \prod_{s=1}^{n} q_s"
ORING_AUTOMATED = r"Y(k) = \theta^k \left( \frac{ah}{n-k} \right)^{n-k}"
ORING_OPTIMAL = r"m^* = \frac{ah}{\theta e}"
ORING_THRESHOLD = r"\bar{\theta}(m) = \frac{ah}{m} \left( \frac{m-1}{m} \right)^{m-1}"

# --- Capital Market ---
CES_PRODUCTION_CAP = r"Y = A \left( a K^{\rho} + (1-a) L^{\rho} \right)^{1/\rho}, \quad \rho = \frac{\sigma-1}{\sigma}"
MPK_EQUATION = r"MPK = A \cdot a \cdot K^{\rho-1} \left( a K^{\rho} + (1-a) L^{\rho} \right)^{1/\rho - 1}"
CAPITAL_SUPPLY = r"r_{\text{required}} = \delta + \rho_{\text{impatience}}"
