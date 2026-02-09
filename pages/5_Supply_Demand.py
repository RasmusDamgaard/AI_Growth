import streamlit as st
import numpy as np
import plotly.graph_objects as go

from models.capital_market import (
    mpk, capital_supply, equilibrium_K, ces_output, capital_share, rho_from_sigma,
)
from utils.plotting import base_figure, COLORS
from utils.latex import CES_PRODUCTION_CAP, MPK_EQUATION, CAPITAL_SUPPLY

st.set_page_config(page_title="Supply & Demand", layout="wide")
st.title("Supply & Demand for Capital")
st.markdown("""
Based on **Albrecht (Economic Forces)** — how AI changes capital market equilibrium
depends on the elasticity of substitution between capital and labor, and on AI hardware depreciation rates.
""")

with st.expander("Key Equations", expanded=False):
    cols = st.columns(3)
    with cols[0]:
        st.latex(CES_PRODUCTION_CAP)
        st.caption("CES production")
    with cols[1]:
        st.latex(MPK_EQUATION)
        st.caption("Capital demand")
    with cols[2]:
        st.latex(CAPITAL_SUPPLY)
        st.caption("Capital supply")

# --- Presets ---
st.sidebar.header("Capital Market Parameters")
preset = st.sidebar.radio("Scenario Preset", [
    "Custom",
    "Complementarity (σ=0.5, δ=0.10)",
    "Transitional Substitution (σ=1.2, δ=0.30)",
    "Zero-Labor Endpoint (σ=2.0, δ=0.20)",
])

if preset.startswith("Complementarity"):
    sigma_default, delta_default = 0.5, 0.10
elif preset.startswith("Transitional"):
    sigma_default, delta_default = 1.2, 0.30
elif preset.startswith("Zero-Labor"):
    sigma_default, delta_default = 2.0, 0.20
else:
    sigma_default, delta_default = 1.0, 0.10

sigma = st.sidebar.slider("Elasticity of substitution (σ)", 0.2, 3.0, sigma_default, 0.05)
cap_weight = st.sidebar.slider("Capital weight (a)", 0.1, 0.9, 0.4, 0.05)
tfp = st.sidebar.slider("TFP (A)", 0.5, 5.0, 1.0, 0.1)
delta = st.sidebar.slider("Depreciation (δ)", 0.01, 0.50, delta_default, 0.01)
impatience = st.sidebar.slider("Impatience rate (ρ)", 0.01, 0.10, 0.03, 0.01)
L = st.sidebar.slider("Labor (L)", 0.5, 5.0, 1.0, 0.1)

# --- Compute ---
rho = rho_from_sigma(sigma)
r_req = capital_supply(delta, impatience)
K_star = equilibrium_K(L, cap_weight, rho, delta, impatience, tfp)

if not np.isnan(K_star):
    Y_star = ces_output(np.array([K_star]), L, cap_weight, rho, tfp)[0]
    cap_share_val = capital_share(K_star, L, cap_weight, rho, tfp)
else:
    Y_star = np.nan
    cap_share_val = np.nan

col1, col2, col3, col4 = st.columns(4)
col1.metric("K*", f"{K_star:.2f}" if not np.isnan(K_star) else "N/A")
col2.metric("Y*", f"{Y_star:.2f}" if not np.isnan(Y_star) else "N/A")
col3.metric("Capital Share", f"{cap_share_val:.1%}" if not np.isnan(cap_share_val) else "N/A")
col4.metric("Required Return", f"{r_req:.1%}")

# --- Charts ---
c1, c2 = st.columns(2)

# Chart 1: Supply & Demand diagram
with c1:
    K_max = max(K_star * 3, 5) if not np.isnan(K_star) else 10
    K_range = np.linspace(0.1, K_max, 500)
    mpk_vals = mpk(K_range, L, cap_weight, rho, tfp)
    fig = base_figure("Capital Market Equilibrium", "Capital (K)", "Return / MPK")
    fig.add_trace(go.Scatter(x=K_range, y=mpk_vals, name="Capital Demand (MPK)",
                             line=dict(color=COLORS[0], width=2)))
    fig.add_hline(y=r_req, line_dash="solid", line_color=COLORS[1],
                  annotation_text=f"Supply: r = {r_req:.1%}")
    if not np.isnan(K_star):
        fig.add_trace(go.Scatter(x=[K_star], y=[r_req], mode="markers",
                                 marker=dict(size=14, color="red", symbol="star"),
                                 name=f"Equilibrium K*={K_star:.1f}"))
    fig.update_layout(yaxis_range=[0, min(float(np.nanmax(mpk_vals)) * 1.1, 5)])
    st.plotly_chart(fig, use_container_width=True)

# Chart 2: Factor shares vs σ
with c2:
    sigmas = np.linspace(0.2, 3.0, 80)
    cap_shares = []
    for s_val in sigmas:
        rho_val = rho_from_sigma(s_val)
        K_eq = equilibrium_K(L, cap_weight, rho_val, delta, impatience, tfp)
        if not np.isnan(K_eq):
            cap_shares.append(capital_share(K_eq, L, cap_weight, rho_val, tfp))
        else:
            cap_shares.append(np.nan)
    cap_shares = np.array(cap_shares)
    lab_shares = 1 - cap_shares

    fig2 = base_figure("Factor Shares vs Elasticity of Substitution", "σ", "Share of Income")
    fig2.add_trace(go.Scatter(x=sigmas, y=cap_shares, name="Capital share",
                              line=dict(color=COLORS[0], width=2), fill="tozeroy"))
    fig2.add_trace(go.Scatter(x=sigmas, y=lab_shares, name="Labor share",
                              line=dict(color=COLORS[1], width=2)))
    fig2.add_vline(x=sigma, line_dash="dash", line_color="red",
                   annotation_text=f"Current σ={sigma}")
    fig2.update_layout(yaxis_range=[0, 1])
    st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Depreciation sensitivity
st.subheader("Depreciation Sensitivity")
deltas = np.linspace(0.01, 0.50, 60)
K_stars_d = []
Y_stars_d = []
cap_shares_d = []
for d in deltas:
    K_eq = equilibrium_K(L, cap_weight, rho, d, impatience, tfp)
    if not np.isnan(K_eq):
        K_stars_d.append(K_eq)
        Y_stars_d.append(ces_output(np.array([K_eq]), L, cap_weight, rho, tfp)[0])
        cap_shares_d.append(capital_share(K_eq, L, cap_weight, rho, tfp))
    else:
        K_stars_d.append(np.nan)
        Y_stars_d.append(np.nan)
        cap_shares_d.append(np.nan)

c3a, c3b, c3c = st.columns(3)
with c3a:
    fig3a = base_figure("K* vs Depreciation", "δ", "Equilibrium Capital K*", height=350)
    fig3a.add_trace(go.Scatter(x=deltas, y=K_stars_d, line=dict(color=COLORS[0], width=2), showlegend=False))
    fig3a.add_vline(x=0.30, line_dash="dot", line_color="orange",
                    annotation_text="GPU obsolescence")
    st.plotly_chart(fig3a, use_container_width=True)

with c3b:
    fig3b = base_figure("Y* vs Depreciation", "δ", "Equilibrium Output Y*", height=350)
    fig3b.add_trace(go.Scatter(x=deltas, y=Y_stars_d, line=dict(color=COLORS[1], width=2), showlegend=False))
    fig3b.add_vline(x=0.30, line_dash="dot", line_color="orange",
                    annotation_text="GPU obsolescence")
    st.plotly_chart(fig3b, use_container_width=True)

with c3c:
    fig3c = base_figure("Capital Share vs Depreciation", "δ", "Capital Share", height=350)
    fig3c.add_trace(go.Scatter(x=deltas, y=cap_shares_d, line=dict(color=COLORS[3], width=2), showlegend=False))
    fig3c.add_vline(x=0.30, line_dash="dot", line_color="orange",
                    annotation_text="GPU obsolescence")
    fig3c.update_layout(yaxis_range=[0, 1])
    st.plotly_chart(fig3c, use_container_width=True)

st.markdown("""
---
**Key Insight:** When σ > 1 (capital and labor are substitutes), the capital share rises
as AI capital becomes more productive. High depreciation rates for AI hardware (GPUs depreciate
~30%/year) partially counteract this by raising the required return, limiting capital accumulation.
""")
