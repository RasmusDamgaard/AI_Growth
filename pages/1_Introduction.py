import streamlit as st

st.set_page_config(page_title="Introduction", layout="wide")
st.title("AI & Economic Growth: Research Overview")

st.markdown("""
This dashboard explores how artificial intelligence may reshape economic growth,
drawing on five academic papers and two substack articles that span growth theory,
task-based models of automation, and capital market dynamics.
""")

# --- Paper summary table ---
st.subheader("Literature Overview")

papers = [
    {
        "Paper": "Jones (2010) — Intermediate Goods",
        "Mechanism": "Intermediate goods in production create a multiplier that amplifies TFP differences",
        "Key Finding": "With α=1/3, σ=1/2, a 2x TFP gap → 8x income gap (multiplier = 3)",
        "Dashboard Page": "Solow Model",
    },
    {
        "Paper": "Jones & Tonetti — Weak Links",
        "Mechanism": "CES task aggregation with σ<1; capital productivity grows faster than labor → endogenous automation",
        "Key Finding": "GDP ~19% above baseline by 2060; weak-link complementarity limits automation gains",
        "Dashboard Page": "Weak Links",
    },
    {
        "Paper": "Gans & Goldfarb — Jagged Frontier",
        "Mechanism": "AI capabilities are uneven across tasks — the 'jagged frontier' means some tasks are automated while similar ones are not",
        "Key Finding": "Task-level heterogeneity in AI capability creates complex adoption patterns",
        "Dashboard Page": "O-Ring / Focus Effect",
    },
    {
        "Paper": "Gans & Goldfarb — O-Ring Automation",
        "Mechanism": "Multiplicative (O-ring) production + focus effect: automating some tasks raises quality on remaining manual tasks",
        "Key Finding": "Workers can benefit from partial automation; last tasks need ever-higher machine quality θ̄(m)",
        "Dashboard Page": "O-Ring / Focus Effect",
    },
    {
        "Paper": "Restrepo — We Won't Be Missed",
        "Mechanism": "If AI substitutes for labor across enough tasks, growth rate can approach compute growth rate",
        "Key Finding": "Upper bound on AI-driven growth determined by rate of compute improvement",
        "Dashboard Page": "Growth Scenarios",
    },
]

st.table(papers)

# --- Substack articles ---
st.subheader("Substack Articles (Economic Forces)")

st.markdown("""
| Article | Key Argument |
|---------|-------------|
| [AI & Labor Share](https://www.economicforces.xyz/p/ai-labor-share) | When σ > 1, AI capital substitutes for labor → capital share rises. High depreciation (GPUs ~30%/yr) partially offsets this. |
| [Complementarities, Weak Links, AI](https://www.economicforces.xyz/p/complementarities-weak-links-ai-and) | Task complementarities (σ < 1) mean the hardest-to-automate tasks become bottlenecks, limiting aggregate AI impact. |
""")

# --- Navigation guide ---
st.subheader("Dashboard Navigation")

st.markdown("""
| Page | What You'll Find |
|------|-----------------|
| **Solow Model** | Classic growth diagram + intermediate goods multiplier. See how TFP differences amplify into income gaps. |
| **Weak Links** | CES task model. Experiment with elasticity of substitution and automation speed. See how weak links constrain growth. |
| **O-Ring / Focus Effect** | Multiplicative production. Visualize the focus effect and rising automation threshold. |
| **Supply & Demand** | Capital market equilibrium. Toggle between complementarity, substitution, and zero-labor scenarios. |
| **Growth Scenarios** | Three comparative trajectories (baseline, moderate, aggressive). See growth rates, labor shares, and automation paths. |

Use the **sidebar sliders** on each page to adjust model parameters and watch the charts update in real time.
""")
