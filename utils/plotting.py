import plotly.graph_objects as go
import plotly.express as px


COLORS = px.colors.qualitative.Set2
TEMPLATE = "plotly_white"


def base_figure(title: str, xaxis: str = "", yaxis: str = "", height: int = 450) -> go.Figure:
    """Return a consistently styled Plotly figure."""
    fig = go.Figure()
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center"),
        xaxis_title=xaxis,
        yaxis_title=yaxis,
        template=TEMPLATE,
        height=height,
        margin=dict(l=60, r=30, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


def add_vline(fig: go.Figure, x: float, label: str = "", color: str = "red"):
    fig.add_vline(x=x, line_dash="dash", line_color=color,
                  annotation_text=label, annotation_position="top right")


def add_hline(fig: go.Figure, y: float, label: str = "", color: str = "red"):
    fig.add_hline(y=y, line_dash="dash", line_color=color,
                  annotation_text=label, annotation_position="top right")
