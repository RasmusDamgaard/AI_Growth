import streamlit as st

st.set_page_config(
    page_title="AI & Economic Growth",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("AI & Economic Growth Dashboard")

st.markdown("""
This interactive dashboard explores how artificial intelligence affects economic growth,
drawing on recent research in growth theory, task-based models, and capital market dynamics.

**Navigate using the sidebar** to explore different models and frameworks:

1. **Introduction** — Overview of the research landscape
2. **Solow Model** — Growth with intermediate goods (Jones 2010)
3. **Weak Links** — CES task automation (Jones & Tonetti)
4. **O-Ring / Focus Effect** — Multiplicative production & automation (Gans & Goldfarb)
5. **Supply & Demand** — Capital market equilibrium under AI
6. **Growth Scenarios** — Comparative trajectory simulations

Each page includes interactive controls to experiment with model parameters
and see how they affect economic outcomes in real time.
""")

st.info("👈 Select a page from the sidebar to get started.")
