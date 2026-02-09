import streamlit as st
import numpy as np
import plotly.graph_objects as go

from models.o_ring import (
    output_curve, net_surplus, optimal_k, optimal_manual_tasks,
    rising_threshold, time_allocation, wage_under_automation,
    profit_under_automation, oring_output_automated,
)
from utils.plotting import base_figure, COLORS
from utils.latex import ORING_PRODUCTION, ORING_AUTOMATED, ORING_OPTIMAL, ORING_THRESHOLD

st.set_page_config(page_title="O-Ring / Focus Effect", layout="wide")
st.title("O-Ring Production & Focus Effect")
st.markdown("""
Based on **Gans & Goldfarb** — in multiplicative (O-ring) production, automating some tasks
lets workers *focus* on fewer remaining tasks, raising quality on each. But the last tasks
to automate require ever-higher machine quality.
""")

with st.expander("Key Equations", expanded=False):
    cols = st.columns(4)
    with cols[0]:
        st.latex(ORING_PRODUCTION)
        st.caption("O-ring production")
    with cols[1]:
        st.latex(ORING_AUTOMATED)
        st.caption("Partial automation")
    with cols[2]:
        st.latex(ORING_OPTIMAL)
        st.caption("Optimal manual tasks")
    with cols[3]:
        st.latex(ORING_THRESHOLD)
        st.caption("Rising quality threshold")

# --- Controls ---
st.sidebar.header("O-Ring Parameters")
n = st.sidebar.slider("Total tasks (n)", 3, 20, 10)
a = st.sidebar.slider("Labor productivity (a)", 0.5, 3.0, 1.0, 0.1)
h = st.sidebar.slider("Hours (h)", 1.0, 16.0, 8.0, 0.5)
theta = st.sidebar.slider("Machine quality (θ)", 0.5, 3.0, 1.2, 0.05)
r = st.sidebar.slider("Rental cost (r)", 0.0, 2.0, 0.1, 0.01)
beta = st.sidebar.slider("Bargaining weight (β)", 0.0, 1.0, 0.5, 0.05)

# --- Compute ---
ks, ys = output_curve(n, a, h, theta)
k_opt = optimal_k(n, a, h, theta, r)
m_star = optimal_manual_tasks(a, h, theta)

col1, col2, col3 = st.columns(3)
col1.metric("Optimal k*", k_opt)
col2.metric("Optimal manual tasks (continuous)", f"{m_star:.1f}")
col3.metric("Y(k*)", f"{oring_output_automated(k_opt, n, a, h, theta):.2f}")

# --- Charts ---
c1, c2 = st.columns(2)

# Chart 1: Output and net surplus vs k
with c1:
    surpluses = np.array([net_surplus(int(k), n, a, h, theta, r) for k in ks])
    fig = base_figure("Output & Net Surplus vs Automated Tasks", "Automated tasks (k)", "Value")
    fig.add_trace(go.Scatter(x=ks, y=ys, name="Y(k)", mode="lines+markers",
                             line=dict(color=COLORS[0], width=2)))
    fig.add_trace(go.Scatter(x=ks, y=surpluses, name="S(k) = Y(k) - rk", mode="lines+markers",
                             line=dict(color=COLORS[1], width=2)))
    fig.add_trace(go.Scatter(x=[k_opt], y=[net_surplus(k_opt, n, a, h, theta, r)],
                             mode="markers", marker=dict(size=14, color="red", symbol="star"),
                             name=f"Optimal k*={k_opt}"))
    st.plotly_chart(fig, use_container_width=True)

# Chart 2: Focus effect — time allocation
with c2:
    k_show = min(k_opt, n - 1) if k_opt > 0 else max(1, n // 2)
    before, after = time_allocation(k_show, n, h)
    task_labels = [f"Task {i+1}" for i in range(n)]
    fig2 = base_figure("Focus Effect: Time Allocation", "Task", "Hours")
    fig2.add_trace(go.Bar(x=task_labels, y=before, name="Before automation",
                          marker_color=COLORS[2], opacity=0.6))
    fig2.add_trace(go.Bar(x=task_labels, y=after, name=f"After automating {k_show} tasks",
                          marker_color=COLORS[0]))
    fig2.update_layout(barmode="group")
    st.plotly_chart(fig2, use_container_width=True)

c3, c4 = st.columns(2)

# Chart 3: Rising quality threshold
with c3:
    m_vals = np.linspace(1, n, 200)
    theta_bar = rising_threshold(m_vals, a, h)
    fig3 = base_figure("Rising Quality Threshold", "Remaining manual tasks (m)", "Min. machine quality θ̄")
    fig3.add_trace(go.Scatter(x=m_vals, y=theta_bar, name="θ̄(m)",
                              line=dict(color=COLORS[3], width=2)))
    fig3.add_hline(y=theta, line_dash="dash", line_color="red",
                   annotation_text=f"Current θ={theta}")
    fig3.update_layout(yaxis_range=[0, max(np.nanmax(theta_bar) * 1.1, theta * 2)])
    st.plotly_chart(fig3, use_container_width=True)

# Chart 4: Wage and profit under automation
with c4:
    wages = np.array([wage_under_automation(int(k), n, a, h, theta, beta) for k in ks])
    profits = np.array([profit_under_automation(int(k), n, a, h, theta, r, beta) for k in ks])
    fig4 = base_figure("Wages & Profits vs Automation", "Automated tasks (k)", "Value")
    fig4.add_trace(go.Scatter(x=ks, y=wages, name=f"W(k) = β·Y(k), β={beta}",
                              line=dict(color=COLORS[0], width=2)))
    fig4.add_trace(go.Scatter(x=ks, y=profits, name="Π(k) = (1-β)·Y(k) - rk",
                              line=dict(color=COLORS[1], width=2)))
    fig4.add_vline(x=k_opt, line_dash="dash", line_color="red",
                   annotation_text=f"k*={k_opt}")
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("""
---
**Key Insight:** Workers can *benefit* from partial automation in O-ring production.
Automating some tasks lets workers focus their time on fewer remaining tasks, raising quality
on each. But the last tasks are hardest to automate — the required machine quality rises
steeply as the number of remaining manual tasks falls.
""")
