"""
Shared utilities: data loading, Plotly theme, and KPI card helpers.
"""
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ── Plotly dark theme ──────────────────────────────────────────────────────────
PLOT_BG      = "#161b22"
PAPER_BG     = "#161b22"
GRID_COLOR   = "#21262d"
TEXT_COLOR   = "#c9d1d9"
AXIS_COLOR   = "#8b949e"
FONT_FAMILY  = "DM Sans, sans-serif"

PALETTE = [
    "#58a6ff",  # blue
    "#3fb950",  # green
    "#f78166",  # coral
    "#d2a8ff",  # purple
    "#ffa657",  # amber
    "#79c0ff",  # light blue
    "#56d364",  # light green
    "#ff7b72",  # red
    "#e3b341",  # yellow
    "#bc8cff",  # lavender
]

INTENSITY_COLORS = {"Low": "#58a6ff", "Medium": "#ffa657", "High": "#f78166"}


def apply_dark_theme(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        height=height,
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family=FONT_FAMILY, color=TEXT_COLOR, size=12),
        title=dict(font=dict(family=FONT_FAMILY, size=14, color="#e6edf3"), x=0, pad=dict(l=4, t=4)),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            font=dict(size=11, color=TEXT_COLOR),
        ),
        margin=dict(l=48, r=16, t=36, b=40),
        xaxis=dict(
            gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
            tickfont=dict(color=AXIS_COLOR, size=11),
            title_font=dict(color=AXIS_COLOR, size=11),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR, linecolor=GRID_COLOR,
            tickfont=dict(color=AXIS_COLOR, size=11),
            title_font=dict(color=AXIS_COLOR, size=11),
            zeroline=False,
        ),
        hoverlabel=dict(
            bgcolor="#1c2128",
            bordercolor="#30363d",
            font=dict(color="#e6edf3", size=12),
        ),
    )
    return fig


@st.cache_data(show_spinner="Loading dataset…")
def load_data() -> pd.DataFrame:
    df = pd.read_csv("health_fitness_dataset.csv")
    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 29, 39, 49, 59, 65],
        labels=["18–29", "30–39", "40–49", "50–59", "60+"],
    )
    df["bmi_cat"] = pd.cut(
        df["bmi"],
        bins=[0, 18.5, 25, 30, 100],
        labels=["Underweight", "Normal", "Overweight", "Obese"],
    )
    df["bp_cat"] = pd.cut(
        df["blood_pressure_systolic"],
        bins=[0, 120, 130, 140, 999],
        labels=["Normal", "Elevated", "High", "Very High"],
        right=False,
    )
    df["cal_per_min"] = df["calories_burned"] / df["duration_minutes"].replace(0, 1)
    df["health_condition"] = df["health_condition"].fillna("None")
    return df


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        activity = st.multiselect(
            "Activity type",
            sorted(df["activity_type"].dropna().unique()),
            default=sorted(df["activity_type"].dropna().unique()),
        )
        intensity = st.multiselect(
            "Intensity",
            sorted(df["intensity"].dropna().unique()),
            default=sorted(df["intensity"].dropna().unique()),
        )
        gender = st.multiselect(
            "Gender",
            sorted(df["gender"].dropna().unique()),
            default=sorted(df["gender"].dropna().unique()),
        )
        age_range = st.slider("Age range", 18, 64, (18, 64))

    mask = (
        df["activity_type"].isin(activity)
        & df["intensity"].isin(intensity)
        & df["gender"].isin(gender)
        & df["age"].between(*age_range)
    )
    return df[mask].copy()


def kpi_row(metrics: list[dict]) -> None:
    """
    metrics: list of dict with keys: label, value, delta (optional), color (optional)
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        delta = m.get("delta", "")
        color = m.get("color", "#58a6ff")
        col.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{m['label']}</div>
                <div class="kpi-value" style="color:{color}">{m['value']}</div>
                {"<div class='kpi-delta'>" + delta + "</div>" if delta else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )


def section(title: str, subtitle: str, color: str = "#58a6ff") -> None:
    st.markdown(
        f'<div class="section-header" style="border-color:{color}">{title}</div>'
        f'<div class="section-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def chart_wrap(fig: go.Figure, key: str | None = None) -> None:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown("</div>", unsafe_allow_html=True)


def insight(text: str) -> None:
    st.markdown(f'<div class="insight-pill">{text}</div>', unsafe_allow_html=True)
