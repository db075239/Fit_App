"""
Dashboard 2 — Exercise Impact on Mental & Physical Health
Key questions answered:
  - Does intensity truly reduce stress? 
  - How does blood pressure vary by activity type?
  - What is the heart rate zone map across intensity levels?
  - Is there a sleep–stress relationship in this dataset?
  - How does smoking status affect resting heart rate?
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import (
    PALETTE, INTENSITY_COLORS, PLOT_BG, PAPER_BG, GRID_COLOR, TEXT_COLOR,
    AXIS_COLOR, FONT_FAMILY, apply_dark_theme, load_data, sidebar_filters,
    section, chart_wrap, insight, kpi_row,
)


def render():
    df_full = load_data()
    df = sidebar_filters(df_full)

    st.markdown(
        """
        <div style="margin-bottom:1.4rem">
            <span style="font-family:'DM Serif Display',serif;font-size:32px;color:#e6edf3;">
                Exercise &amp; Health Impact
            </span><br>
            <span style="font-size:13px;color:#8b949e;letter-spacing:0.3px;">
                How physical activity shapes stress, cardiovascular markers, and sleep quality
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI row ────────────────────────────────────────────────────────────────
    kpi_row([
        {"label": "Avg Stress Score",     "value": f"{df['stress_level'].mean():.2f} / 10",          "color": "#f78166"},
        {"label": "Avg Resting HR",       "value": f"{df['resting_heart_rate'].mean():.1f} bpm",      "color": "#58a6ff"},
        {"label": "Avg Systolic BP",      "value": f"{df['blood_pressure_systolic'].mean():.0f} mmHg","color": "#ffa657"},
        {"label": "Avg Sleep",            "value": f"{df['hours_sleep'].mean():.2f} hrs",              "color": "#3fb950"},
        {"label": "Never Smoked",         "value": f"{(df['smoking_status']=='Never').mean()*100:.0f}%","color": "#d2a8ff"},
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Stress by intensity (honest flat result) + BP by activity ───────
    section(
        "Does workout intensity reduce stress?",
        "Honest finding: stress levels are nearly identical across Low, Medium, and High intensity — a valuable null result",
        color="#f78166",
    )

    c1, c2 = st.columns(2)

    with c1:
        stress_int = (
            df.groupby(["activity_type", "intensity"], as_index=False)["stress_level"]
            .mean()
        )
        fig1 = px.bar(
            stress_int,
            x="activity_type",
            y="stress_level",
            color="intensity",
            barmode="group",
            color_discrete_map=INTENSITY_COLORS,
            text_auto=".1f",
        )
        apply_dark_theme(fig1, height=360)
        fig1.update_layout(
            title="Stress level by activity × intensity",
            xaxis_title=None,
            yaxis_title="Avg stress (1–10)",
            xaxis_tickangle=-35,
            yaxis=dict(range=[0, 8], gridcolor=GRID_COLOR),
            legend_title_text="Intensity",
        )
        fig1.update_traces(textfont_size=9, textposition="outside")
        chart_wrap(fig1, "stress_intensity")

    with c2:
        bp_act = (
            df.groupby("activity_type", as_index=False)
            .agg(
                systolic_median=("blood_pressure_systolic", "median"),
                systolic_q1=("blood_pressure_systolic", lambda x: x.quantile(0.25)),
                systolic_q3=("blood_pressure_systolic", lambda x: x.quantile(0.75)),
            )
            .sort_values("systolic_median", ascending=False)
        )
        fig2 = go.Figure()
        for i, row in bp_act.iterrows():
            fig2.add_trace(go.Bar(
                x=[row["activity_type"]],
                y=[row["systolic_median"]],
                error_y=dict(
                    type="data",
                    symmetric=False,
                    array=[row["systolic_q3"] - row["systolic_median"]],
                    arrayminus=[row["systolic_median"] - row["systolic_q1"]],
                    color="#30363d",
                    thickness=1.5,
                    width=4,
                ),
                marker=dict(color=PALETTE[i % len(PALETTE)], line=dict(width=0)),
                name=row["activity_type"],
                showlegend=False,
                hovertemplate=f"<b>{row['activity_type']}</b><br>Median: {row['systolic_median']:.0f} mmHg<extra></extra>",
            ))
        # Reference lines
        for bp_val, label, color in [(120, "Normal", "#3fb950"), (130, "Elevated", "#ffa657"), (140, "High", "#f78166")]:
            fig2.add_hline(
                y=bp_val,
                line_dash="dot",
                line_color=color,
                line_width=1,
                annotation_text=label,
                annotation_font=dict(size=10, color=color),
                annotation_position="right",
            )
        apply_dark_theme(fig2, height=360)
        fig2.update_layout(
            title="Median systolic blood pressure by activity",
            xaxis_title=None,
            yaxis_title="Systolic BP (mmHg)",
            xaxis_tickangle=-35,
            yaxis=dict(range=[110, 145], gridcolor=GRID_COLOR),
        )
        chart_wrap(fig2, "bp_activity")

    c1i, c2i = st.columns(2)
    with c1i:
        insight("⚠️ <strong>Stress is flat across intensities</strong> (~5.25/10 regardless of Low/Medium/High). ")
    with c2i:
        insight("💡 <strong>Blood pressure clusters near 120 mmHg</strong> across all activities. No activity type consistently pushes BP into hypertensive territory.")

    # ── Row 2: Sleep distribution + Stress histogram ───────────────────────────
    section(
        "Sleep quality and stress distribution",
        "Understanding the population's baseline sleep and stress profiles",
        color="#3fb950",
    )

    c3, c4 = st.columns(2)

    with c3:
        fig3 = go.Figure()
        fig3.add_trace(go.Histogram(
            x=df["hours_sleep"].sample(min(50000, len(df)), random_state=1),
            nbinsx=30,
            marker=dict(color="#3fb950", line=dict(color=PLOT_BG, width=0.5)),
            opacity=0.85,
            hovertemplate="<b>%{x:.1f} hrs sleep</b><br>%{y:,} records<extra></extra>",
        ))
        fig3.add_vline(x=7, line_dash="dot", line_color="#58a6ff", line_width=1.5,
                       annotation_text="Rec. 7 hrs", annotation_font=dict(size=10, color="#58a6ff"))
        apply_dark_theme(fig3, height=320)
        fig3.update_layout(
            title="Sleep hours distribution",
            xaxis_title="Hours of sleep",
            yaxis_title="Record count",
        )
        chart_wrap(fig3, "sleep_hist")

    with c4:
        fig4 = go.Figure()
        fig4.add_trace(go.Histogram(
            x=df["stress_level"],
            nbinsx=10,
            marker=dict(
                color=["#3fb950", "#3fb950", "#3fb950", "#3fb950",
                       "#ffa657", "#ffa657", "#ffa657",
                       "#f78166", "#f78166", "#f78166"],
                line=dict(color=PLOT_BG, width=1),
            ),
            opacity=0.85,
            hovertemplate="<b>Stress level %{x}</b><br>%{y:,} records<extra></extra>",
        ))
        apply_dark_theme(fig4, height=320)
        fig4.update_layout(
            title="Stress level distribution (1–10 scale)",
            xaxis_title="Stress level",
            yaxis_title="Record count",
            xaxis=dict(dtick=1),
        )
        chart_wrap(fig4, "stress_hist")

    # ── Row 3: Smoking vs HR + Sleep–Stress heatmap ────────────────────────────
    section(
        "Lifestyle factors: smoking and sleep patterns",
        "Smoking status shows minimal resting HR difference",
        color="#d2a8ff",
    )

    c5, c6 = st.columns(2)

    with c5:
        smoke_metrics = (
            df.groupby("smoking_status", as_index=False)
            .agg(
                resting_hr=("resting_heart_rate", "mean"),
                systolic=("blood_pressure_systolic", "mean"),
                fitness=("fitness_level", "mean"),
            )
        )
        fig5 = go.Figure()
        categories = ["Resting HR (bpm)", "Systolic BP (mmHg)", "Fitness Level"]
        colors_smoke = {"Never": "#3fb950", "Former": "#ffa657", "Current": "#f78166"}
        for _, row in smoke_metrics.iterrows():
            vals = [
                row["resting_hr"],
                row["systolic"] / 10,   # scaled for radar
                row["fitness"],
            ]
            fig5.add_trace(go.Bar(
                x=["Resting HR", "Systolic BP\n(÷10)", "Fitness level"],
                y=[row["resting_hr"], row["systolic"] / 10, row["fitness"]],
                name=row["smoking_status"],
                marker=dict(color=colors_smoke.get(row["smoking_status"], PALETTE[0]), line=dict(width=0)),
                hovertemplate="<b>%{x}</b><br>%{y:.2f}<extra></extra>",
            ))
        apply_dark_theme(fig5, height=320)
        fig5.update_layout(
            title="Key health markers by smoking status",
            barmode="group",
            xaxis_title=None,
            yaxis_title="Value",
            legend_title_text="Smoking status",
        )
        chart_wrap(fig5, "smoking_bar")

    with c6:
        # Sleep vs Stress 2D density
        sample = df.sample(min(30000, len(df)), random_state=42)
        fig6 = go.Figure(go.Histogram2dContour(
            x=sample["hours_sleep"],
            y=sample["stress_level"],
            colorscale=[[0, PLOT_BG], [0.2, "#1f3a5f"], [0.6, "#58a6ff"], [1, "#f78166"]],
            ncontours=15,
            contours=dict(showlabels=False),
            line=dict(width=0.5),
            hovertemplate="Sleep: %{x:.1f}h<br>Stress: %{y}<extra></extra>",
        ))
        apply_dark_theme(fig6, height=320)
        fig6.update_layout(
            title="Sleep vs stress density map",
            xaxis_title="Hours of sleep",
            yaxis_title="Stress level (1–10)",
            yaxis=dict(dtick=2),
        )
        chart_wrap(fig6, "sleep_stress_density")

    c5i, c6i = st.columns(2)
    with c5i:
        insight("⚠️ <strong>Smoking vs resting HR difference is <2 bpm</strong> — this dataset captures single-session snapshots, not long-term physiological changes from smoking.")
    with c6i:
        insight("💡 <strong>Sleep and stress are nearly uniformly distributed</strong> — no strong linear relationship. Stress levels range evenly 1–10 regardless of sleep duration.")

    # ── Row 4: Age group × stress violin ──────────────────────────────────────
    section(
        "Does age affect stress resilience?",
        "Distribution of stress levels across age groups — are older participants calmer?",
        color="#ffa657",
    )

    sample_violin = df.sample(min(20000, len(df)), random_state=7)
    fig7 = go.Figure()
    for i, ag in enumerate(["18–29", "30–39", "40–49", "50–59", "60+"]):
        sub = sample_violin[sample_violin["age_group"].astype(str) == ag]["stress_level"]
        if len(sub) == 0:
            continue
        fig7.add_trace(go.Violin(
            x=[ag] * len(sub),
            y=sub,
            name=ag,
            box_visible=True,
            meanline_visible=True,
            fillcolor=PALETTE[i],
            line_color=PALETTE[i],
            opacity=0.7,
            points=False,
        ))
    apply_dark_theme(fig7, height=340)
    fig7.update_layout(
        title="Stress level distribution by age group",
        xaxis_title="Age group",
        yaxis_title="Stress level (1–10)",
        showlegend=False,
        yaxis=dict(dtick=2),
    )
    chart_wrap(fig7, "stress_violin")
    insight("💡 <strong>Stress distributions are almost identical across all age groups</strong> — no age group is systematically more or less stressed, suggesting stress is highly individual in this population.")
