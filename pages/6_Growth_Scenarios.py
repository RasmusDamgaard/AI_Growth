import streamlit as st
import numpy as np
import plotly.graph_objects as go

from models.scenarios import simulate_scenario
from utils.plotting import base_figure, COLORS

st.set_page_config(page_title="Growth Scenarios", layout="wide")
st.title("Comparative Growth Scenarios")
st.markdown("""
Synthesizing insights from all models into three growth trajectories:
**Baseline** (no AI acceleration), **Moderate** (weak-links automation with diminishing returns),
and **Aggressive** (compute-driven growth approaching hardware improvement rates).
""")

# --- Controls ---
st.sidebar.header("Scenario Parameters")
g_tfp = st.sidebar.slider("Baseline TFP growth (%/yr)", 0.5, 3.0, 1.0, 0.1) / 100
auto_boost = st.sidebar.slider("Automation TFP boost", 0.01, 0.10, 0.03, 0.005)
auto_speed = st.sidebar.slider("Automation speed", 0.01, 0.20, 0.05, 0.01)
s = st.sidebar.slider("Savings rate (s)", 0.10, 0.40, 0.20, 0.02)
alpha = st.sidebar.slider("Capital share (α)", 0.20, 0.50, 0.33, 0.01)
delta = st.sidebar.slider("Depreciation (δ)", 0.02, 0.15, 0.05, 0.01)
horizon = st.sidebar.slider("Horizon (years)", 20, 100, 50, 5)
compute_g = st.sidebar.slider("Compute growth rate (%/yr)", 5.0, 30.0, 15.0, 1.0) / 100

# --- Simulate ---
baseline = simulate_scenario(g_tfp, auto_boost, auto_speed, s, alpha, delta, horizon,
                             compute_g, "baseline")
moderate = simulate_scenario(g_tfp, auto_boost, auto_speed, s, alpha, delta, horizon,
                             compute_g, "moderate")
aggressive = simulate_scenario(g_tfp, auto_boost, auto_speed, s, alpha, delta, horizon,
                               compute_g, "aggressive")

# Summary metrics
mod_gain = (moderate["y"][-1] / baseline["y"][-1] - 1) * 100
agg_gain = (aggressive["y"][-1] / baseline["y"][-1] - 1) * 100
col1, col2, col3 = st.columns(3)
col1.metric("Moderate vs Baseline (final)", f"+{mod_gain:.0f}%")
col2.metric("Aggressive vs Baseline (final)", f"+{agg_gain:.0f}%")
col3.metric("Aggressive Final Growth Rate", f"{aggressive['g'][-1]*100:.1f}%/yr")

# --- Charts ---
c1, c2 = st.columns(2)

# Chart 1: GDP trajectories (log scale)
with c1:
    fig = base_figure("GDP Trajectories", "Year", "GDP (log scale)")
    for data, name, color, dash in [
        (baseline, "Baseline", COLORS[1], "dash"),
        (moderate, "Moderate (weak links)", COLORS[0], "solid"),
        (aggressive, "Aggressive (Restrepo)", COLORS[3], "solid"),
    ]:
        fig.add_trace(go.Scatter(x=data["t"], y=data["y"], name=name,
                                 line=dict(color=color, width=2, dash=dash)))
    fig.update_layout(yaxis_type="log")

    # Milestone annotations
    mid = horizon // 2
    fig.add_annotation(x=mid, y=moderate["y"][mid],
                       text=f"+{(moderate['y'][mid]/baseline['y'][mid]-1)*100:.0f}%",
                       showarrow=True, arrowhead=2, ax=40, ay=-20)
    st.plotly_chart(fig, use_container_width=True)

# Chart 2: Growth rate over time
with c2:
    fig2 = base_figure("Growth Rate Over Time", "Year", "Annual Growth Rate (%)")
    for data, name, color, dash in [
        (baseline, "Baseline", COLORS[1], "dash"),
        (moderate, "Moderate", COLORS[0], "solid"),
        (aggressive, "Aggressive", COLORS[3], "solid"),
    ]:
        fig2.add_trace(go.Scatter(x=data["t"][1:], y=data["g"][1:] * 100, name=name,
                                  line=dict(color=color, width=2, dash=dash)))
    fig2.add_hline(y=compute_g * 100, line_dash="dot", line_color="gray",
                   annotation_text=f"Compute growth ({compute_g*100:.0f}%/yr)")
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns(2)

# Chart 3: Labor share trajectories
with c3:
    fig3 = base_figure("Labor Share Trajectories", "Year", "Labor Share of Income")
    for data, name, color, dash in [
        (baseline, "Baseline (~65%)", COLORS[1], "dash"),
        (moderate, "Moderate → ~40%", COLORS[0], "solid"),
        (aggressive, "Aggressive → 0%", COLORS[3], "solid"),
    ]:
        fig3.add_trace(go.Scatter(x=data["t"], y=data["labor_share"], name=name,
                                  line=dict(color=color, width=2, dash=dash)))
    fig3.update_layout(yaxis_range=[0, 0.8])
    st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Automation frontier & per-capita output
with c4:
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=moderate["t"], y=moderate["beta"],
                              name="β (moderate)", line=dict(color=COLORS[0], width=2)))
    fig4.add_trace(go.Scatter(x=aggressive["t"], y=aggressive["beta"],
                              name="β (aggressive)", line=dict(color=COLORS[3], width=2)))
    # Secondary axis for output
    fig4.add_trace(go.Scatter(x=moderate["t"], y=moderate["y"],
                              name="Output (moderate)", yaxis="y2",
                              line=dict(color=COLORS[0], width=1, dash="dot")))
    fig4.add_trace(go.Scatter(x=aggressive["t"], y=aggressive["y"],
                              name="Output (aggressive)", yaxis="y2",
                              line=dict(color=COLORS[3], width=1, dash="dot")))
    fig4.update_layout(
        title=dict(text="Automation Frontier & Output", x=0.5),
        xaxis_title="Year",
        yaxis=dict(title="Automation share (β)", range=[0, 1]),
        yaxis2=dict(title="Per-capita output", overlaying="y", side="right", type="log"),
        template="plotly_white", height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
---
**Key Insights:**
- **Baseline:** Steady ~1%/yr TFP growth yields modest income gains.
- **Moderate (Jones & Tonetti):** Endogenous automation boosts growth but faces diminishing returns
  from weak-link complementarities — the hardest tasks remain manual bottlenecks.
- **Aggressive (Restrepo):** If AI growth tracks compute hardware improvement (~15%/yr),
  growth accelerates dramatically — but this requires substitutability (σ > 1) across most tasks.
- Labor's income share declines under all automation scenarios, raising distribution questions.
""")
