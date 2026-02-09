import streamlit as st
import numpy as np
import plotly.graph_objects as go

from models.solow import (
    savings_curve, depreciation_line, steady_state_k, steady_state_y,
    per_capita_production, transition_dynamics, multiplier, multiplier_grid,
    income_ratio,
)
from utils.plotting import base_figure, COLORS, add_vline
from utils.latex import SOLOW_PRODUCTION, SOLOW_STEADY_STATE, SOLOW_MULTIPLIER

st.set_page_config(page_title="Solow Model", layout="wide")
st.title("Solow Model with Intermediate Goods")
st.markdown("Based on **Jones (2010)** — intermediate goods create a multiplier that amplifies TFP differences into large income differences.")

# --- Equations ---
with st.expander("Key Equations", expanded=False):
    cols = st.columns(3)
    with cols[0]:
        st.latex(SOLOW_PRODUCTION)
        st.caption("Production function")
    with cols[1]:
        st.latex(SOLOW_STEADY_STATE)
        st.caption("Steady state income")
    with cols[2]:
        st.latex(SOLOW_MULTIPLIER)
        st.caption("Amplification multiplier")

# --- Sidebar controls ---
st.sidebar.header("Solow Parameters")
A = st.sidebar.slider("TFP (A)", 0.5, 5.0, 1.0, 0.1)
alpha = st.sidebar.slider("Capital share (α)", 0.1, 0.6, 1/3, 0.01)
sigma = st.sidebar.slider("Intermediate goods share (σ)", 0.0, 0.8, 0.5, 0.05)
s = st.sidebar.slider("Savings rate (s)", 0.05, 0.5, 0.2, 0.01)
delta = st.sidebar.slider("Depreciation (δ)", 0.01, 0.15, 0.05, 0.01)
T = st.sidebar.slider("Periods (T)", 20, 200, 100, 10)
k0_frac = st.sidebar.slider("Initial k (fraction of k*)", 0.05, 2.0, 0.1, 0.05)

# --- Compute ---
k_star = steady_state_k(A, alpha, sigma, s, delta)
y_star = steady_state_y(A, alpha, sigma, s, delta)
k_star_basic = steady_state_k(A, alpha, 0.0, s, delta)
m = multiplier(alpha, sigma)

k0 = k0_frac * k_star
k_range = np.linspace(0.01, k_star * 2.5, 500)

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("k*", f"{k_star:.2f}")
col2.metric("y*", f"{y_star:.2f}")
col3.metric("Multiplier", f"{m:.2f}")
col4.metric("k* (no intermediates)", f"{k_star_basic:.2f}")

# --- Charts ---
c1, c2 = st.columns(2)

# Chart 1: Solow diagram
with c1:
    fig = base_figure("Solow Diagram", "Capital per worker (k)", "Investment per worker")
    fig.add_trace(go.Scatter(x=k_range, y=savings_curve(k_range, A, alpha, sigma, s),
                             name=f"Savings (σ={sigma})", line=dict(color=COLORS[0], width=2)))
    fig.add_trace(go.Scatter(x=k_range, y=savings_curve(k_range, A, alpha, 0.0, s),
                             name="Savings (no intermediates)", line=dict(color=COLORS[1], dash="dash", width=2)))
    fig.add_trace(go.Scatter(x=k_range, y=depreciation_line(k_range, delta),
                             name=f"Depreciation (δ={delta})", line=dict(color=COLORS[3], width=2)))
    fig.add_trace(go.Scatter(x=[k_star], y=[delta * k_star], mode="markers",
                             marker=dict(size=12, color="red", symbol="star"),
                             name=f"Steady state k*={k_star:.1f}"))
    st.plotly_chart(fig, use_container_width=True)

# Chart 2: Transition dynamics
with c2:
    k_t, y_t = transition_dynamics(A, alpha, sigma, s, delta, k0, T)
    fig2 = base_figure("Transition Dynamics", "Period", "Per capita value")
    periods = np.arange(T)
    fig2.add_trace(go.Scatter(x=periods, y=k_t, name="Capital (k_t)", line=dict(color=COLORS[0], width=2)))
    fig2.add_trace(go.Scatter(x=periods, y=y_t, name="Output (y_t)", line=dict(color=COLORS[1], width=2)))
    fig2.add_hline(y=k_star, line_dash="dash", line_color="gray", annotation_text="k*")
    fig2.add_hline(y=y_star, line_dash="dot", line_color="gray", annotation_text="y*")
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns(2)

# Chart 3: Multiplier heatmap
with c3:
    alphas = np.linspace(0.1, 0.6, 30)
    sigmas = np.linspace(0.0, 0.8, 30)
    mgrid = multiplier_grid(alphas, sigmas)
    fig3 = go.Figure(data=go.Heatmap(
        z=mgrid, x=alphas, y=sigmas,
        colorscale="YlOrRd", colorbar_title="Multiplier",
        hovertemplate="α=%{x:.2f}<br>σ=%{y:.2f}<br>Multiplier=%{z:.2f}<extra></extra>",
    ))
    fig3.update_layout(
        title=dict(text="Multiplier Heatmap (α vs σ)", x=0.5),
        xaxis_title="Capital share (α)", yaxis_title="Intermediate goods share (σ)",
        template="plotly_white", height=450,
    )
    # Mark empirical calibration point
    fig3.add_trace(go.Scatter(x=[1/3], y=[0.5], mode="markers+text",
                              marker=dict(size=14, color="blue", symbol="x"),
                              text=["Empirical (3x)"], textposition="top right",
                              name="α=1/3, σ=1/2"))
    st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Income differences
with c4:
    tfp_ratio = 2.0
    ratio_basic = income_ratio(tfp_ratio, alpha, 0.0)
    ratio_intermediate = income_ratio(tfp_ratio, alpha, sigma)
    fig4 = base_figure("Income Amplification (2x TFP Difference)", "", "Income Ratio")
    fig4.add_trace(go.Bar(
        x=["Without Intermediates", "With Intermediates"],
        y=[ratio_basic, ratio_intermediate],
        marker_color=[COLORS[1], COLORS[0]],
        text=[f"{ratio_basic:.1f}x", f"{ratio_intermediate:.1f}x"],
        textposition="outside",
    ))
    fig4.update_layout(showlegend=False, yaxis_range=[0, max(ratio_intermediate * 1.3, 10)])
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
---
**Key Insight:** With α=1/3 and σ=1/2, a 2x TFP difference maps to an **8x income difference**
— matching the observed gap between rich and poor countries. Without intermediate goods, the same
TFP difference only produces a ~2.8x income gap.
""")
