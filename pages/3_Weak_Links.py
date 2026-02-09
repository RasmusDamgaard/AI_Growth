import streamlit as st
import numpy as np
import plotly.graph_objects as go

from models.weak_links import simulate_automation, weak_link_demo
from utils.plotting import base_figure, COLORS
from utils.latex import CES_AGGREGATION, TASK_PRODUCTION

st.set_page_config(page_title="Weak Links & Automation", layout="wide")
st.title("Weak Links & Task Automation")
st.markdown("""
Based on **Jones & Tonetti** — when tasks combine with low elasticity of substitution (σ < 1),
the weakest task constrains aggregate output. Capital productivity is growing ~5pp/year faster
than labor, driving endogenous automation of tasks.
""")

with st.expander("Key Equations", expanded=False):
    cols = st.columns(2)
    with cols[0]:
        st.latex(CES_AGGREGATION)
        st.caption("CES task aggregation")
    with cols[1]:
        st.latex(TASK_PRODUCTION)
        st.caption("Task production (linear in K or L)")

# --- Controls ---
st.sidebar.header("Weak Links Parameters")
sigma = st.sidebar.slider("Elasticity of substitution (σ)", 0.1, 2.0, 0.5, 0.05)
n = st.sidebar.slider("Number of tasks (n)", 3, 30, 10)
g_k = st.sidebar.slider("Capital productivity growth (g_k)", 0.01, 0.15, 0.08, 0.01)
g_l = st.sidebar.slider("Labor productivity growth (g_l)", 0.01, 0.10, 0.03, 0.01)
beta_0 = st.sidebar.slider("Initial automation share (β₀)", 0.0, 0.5, 0.1, 0.05)
years = st.sidebar.slider("Years", 10, 100, 50, 5)

# --- Simulation ---
result = simulate_automation(n, sigma, g_k, g_l, beta_0, years)

# End metrics
final_gdp_ratio = result["gdp"][-1] / result["gdp_baseline"][-1]
col1, col2, col3 = st.columns(3)
col1.metric("GDP vs Baseline (final year)", f"{(final_gdp_ratio - 1)*100:.0f}% above")
col2.metric("Final Automation Share", f"{result['beta'][-1]:.0%}")
col3.metric("Final Capital Share", f"{result['capital_share'][-1]:.0%}")

# --- Charts ---
c1, c2 = st.columns(2)

# Chart 1: Task allocation diagram
with c1:
    # Show automation frontier at selected time points
    fig = base_figure("Task Allocation Over Time", "Task index", "")
    time_points = [0, years // 4, years // 2, 3 * years // 4, years - 1]
    for idx, tp in enumerate(time_points):
        beta = result["beta"][tp]
        n_auto = int(round(beta * n))
        colors = ["#e74c3c"] * n_auto + ["#3498db"] * (n - n_auto)
        labels = [f"T{i+1}" for i in range(n)]
        fig.add_trace(go.Bar(
            x=labels, y=[1] * n,
            name=f"Year {tp} (β={beta:.0%})",
            marker_color=colors,
            visible=True if idx == len(time_points) - 1 else "legendonly",
            opacity=0.8,
        ))
    fig.update_layout(
        yaxis_visible=False, barmode="overlay",
        annotations=[
            dict(x=0.5, y=1.15, xref="paper", yref="paper",
                 text="Red = Capital | Blue = Labor", showarrow=False)
        ],
    )
    st.plotly_chart(fig, use_container_width=True)

# Chart 2: Weak link demo
with c2:
    demo = weak_link_demo(n, max(sigma, 0.2), max(sigma + 1.0, 1.5))
    sigma_low = max(sigma, 0.2)
    sigma_high = max(sigma + 1.0, 1.5)
    task_labels = [f"Task {i+1}" for i in range(n)]

    fig2 = base_figure("Weak Link Effect", "Task", "Task Output")
    fig2.add_trace(go.Bar(x=task_labels, y=demo["task_outputs_uniform"],
                          name="Uniform tasks", marker_color=COLORS[0], opacity=0.5))
    fig2.add_trace(go.Bar(x=task_labels, y=demo["task_outputs_weak"],
                          name="One weak task", marker_color=COLORS[3]))
    fig2.update_layout(barmode="group")

    # Add annotations for aggregate output
    fig2.add_annotation(x=0.02, y=0.95, xref="paper", yref="paper",
                        text=(f"σ={sigma_low:.1f}: Uniform→{demo['y_uniform_low']:.1f}, "
                              f"Weak→{demo['y_weak_low']:.1f} "
                              f"({(1-demo['y_weak_low']/demo['y_uniform_low'])*100:.0f}% drop)"),
                        showarrow=False, bgcolor="lightyellow", bordercolor="gray")
    fig2.add_annotation(x=0.02, y=0.82, xref="paper", yref="paper",
                        text=(f"σ={sigma_high:.1f}: Uniform→{demo['y_uniform_high']:.1f}, "
                              f"Weak→{demo['y_weak_high']:.1f} "
                              f"({(1-demo['y_weak_high']/demo['y_uniform_high'])*100:.0f}% drop)"),
                        showarrow=False, bgcolor="lightyellow", bordercolor="gray")
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns(2)

# Chart 3: Growth trajectories
with c3:
    fig3 = base_figure("Growth Trajectories (log scale)", "Year", "GDP (log scale)")
    fig3.add_trace(go.Scatter(x=result["t"], y=result["gdp_baseline"],
                              name="Baseline (fixed β₀)", line=dict(color=COLORS[1], width=2, dash="dash")))
    fig3.add_trace(go.Scatter(x=result["t"], y=result["gdp"],
                              name="Endogenous automation", line=dict(color=COLORS[0], width=2)))
    fig3.add_trace(go.Scatter(x=result["t"], y=result["gdp_full_auto"],
                              name="Full automation", line=dict(color=COLORS[3], width=2, dash="dot")))
    fig3.update_layout(yaxis_type="log")

    # Annotate final gap
    fig3.add_annotation(x=result["t"][-1], y=result["gdp"][-1],
                        text=f"{(final_gdp_ratio-1)*100:.0f}% above baseline",
                        showarrow=True, arrowhead=2, ax=-80, ay=-30)
    st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Capital share over time
with c4:
    fig4 = base_figure("Capital Share of Income", "Year", "Capital Share")
    fig4.add_trace(go.Scatter(x=result["t"], y=result["capital_share"],
                              name="Capital share", line=dict(color=COLORS[0], width=2),
                              fill="tozeroy"))
    fig4.add_trace(go.Scatter(x=result["t"], y=1 - result["capital_share"],
                              name="Labor share", line=dict(color=COLORS[1], width=2)))
    fig4.update_layout(yaxis_range=[0, 1])
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
---
**Key Insight:** When σ < 1 (complementary tasks), the weakest task bottlenecks the entire economy.
As capital productivity grows faster than labor, firms endogenously automate tasks — but weak-link
complementarity means each remaining manual task becomes increasingly critical. The model predicts
GDP ~19% above baseline by 2060 with gradual automation.
""")
