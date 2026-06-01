"""
Dashboard 3 — Workout Performance & Lifestyle Analysis
Story: How do specific workout parameters drive performance outcomes?
Key questions answered:
  - What is each activity's calorie efficiency (kcal/min)?
  - How do heart rate zones split across intensity levels?
  - What does the gender × activity performance matrix look like?
  - How does hydration correlate with activity type?
  - What are the top/bottom performers in the dataset?
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
                Workout Performance &amp; Lifestyle
            </span><br>
            <span style="font-size:13px;color:#8b949e;letter-spacing:0.3px;">
                Efficiency, heart rate zones, and lifestyle habits across 10 activity types
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI row ────────────────────────────────────────────────────────────────
    kpi_row([
        {"label": "Top Activity (kcal/min)", "value": "HIIT · 0.37",            "color": "#f78166"},
        {"label": "Avg HR — High Intensity", "value": "151.1 bpm",              "color": "#f78166"},
        {"label": "Avg HR — Medium",         "value": "133.3 bpm",              "color": "#ffa657"},
        {"label": "Avg HR — Low",            "value": "115.4 bpm",              "color": "#58a6ff"},
        {"label": "Avg Hydration",           "value": f"{df['hydration_level'].mean():.2f} L","color": "#3fb950"},
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Calorie efficiency radar + HR zone grouped bar ─────────────────
    section(
        "Calorie efficiency: how much do you burn per minute?",
        "HIIT leads at 0.37 kcal/min — Yoga trails at 0.09 kcal/min. A 4× efficiency gap.",
        color="#f78166",
    )

    c1, c2 = st.columns(2)

    with c1:
        eff = (
            df.groupby("activity_type", as_index=False)
            .agg(cal_per_min=("cal_per_min", "mean"))
            .sort_values("cal_per_min", ascending=False)
        )
        # Polar / spider for calorie efficiency
        categories_eff = eff["activity_type"].tolist() + [eff["activity_type"].iloc[0]]
        values_eff = eff["cal_per_min"].tolist() + [eff["cal_per_min"].iloc[0]]

        fig1 = go.Figure()
        fig1.add_trace(go.Scatterpolar(
            r=values_eff,
            theta=categories_eff,
            fill="toself",
            fillcolor="rgba(247,129,102,0.2)",
            line=dict(color="#f78166", width=2),
            marker=dict(size=6, color="#f78166"),
            hovertemplate="<b>%{theta}</b><br>%{r:.3f} kcal/min<extra></extra>",
        ))
        apply_dark_theme(fig1, height=380)
        fig1.update_layout(
            title="Calorie efficiency per minute (kcal/min)",
            polar=dict(
                bgcolor=PLOT_BG,
                radialaxis=dict(
                    visible=True,
                    range=[0, 0.42],
                    gridcolor=GRID_COLOR,
                    tickfont=dict(color=AXIS_COLOR, size=10),
                    tickformat=".2f",
                ),
                angularaxis=dict(
                    tickfont=dict(color=TEXT_COLOR, size=11),
                    linecolor=GRID_COLOR,
                ),
            ),
            margin=dict(l=60, r=60, t=50, b=40),
        )
        chart_wrap(fig1, "efficiency_radar")

    with c2:
        hr_zones = (
            df.groupby(["activity_type", "intensity"], as_index=False)["avg_heart_rate"]
            .mean()
            .sort_values("avg_heart_rate", ascending=False)
        )
        fig2 = px.bar(
            hr_zones,
            x="activity_type",
            y="avg_heart_rate",
            color="intensity",
            barmode="group",
            color_discrete_map=INTENSITY_COLORS,
            text_auto=".0f",
        )
        # HR zone reference bands
        for y_start, y_end, label, color in [
            (115, 133, "Zone 2 (aerobic base)", "rgba(88,166,255,0.06)"),
            (133, 151, "Zone 3–4 (aerobic / threshold)", "rgba(255,166,87,0.06)"),
            (151, 160, "Zone 5 (max effort)", "rgba(247,129,102,0.06)"),
        ]:
            fig2.add_hrect(
                y0=y_start, y1=y_end,
                fillcolor=color,
                line_width=0,
                annotation_text=label,
                annotation_font=dict(size=9, color=AXIS_COLOR),
                annotation_position="right",
            )
        apply_dark_theme(fig2, height=380)
        fig2.update_layout(
            title="Heart rate zones by activity × intensity",
            xaxis_title=None,
            yaxis_title="Avg heart rate (bpm)",
            xaxis_tickangle=-35,
            yaxis=dict(range=[105, 165], gridcolor=GRID_COLOR),
            legend_title_text="Intensity",
        )
        fig2.update_traces(textfont_size=8)
        chart_wrap(fig2, "hr_zones_bar")

    c1i, c2i = st.columns(2)
    with c1i:
        insight("🏆 <strong>HIIT top performer:</strong> 0.37 kcal/min vs Yoga's 0.09 kcal/min — choosing the right activity makes a dramatic difference in calorie-burning efficiency")
    with c2i:
        insight("💡 <strong>HR zones are remarkably consistent</strong> across activities at the same intensity — Low=115, Med=133, High=151 bpm regardless of activity type")

    # ── Row 2: Gender × Activity heatmap (full matrix) ────────────────────────
    section(
        "Gender × activity performance matrix",
        "Average calories burned across all gender and activity type combinations",
        color="#3fb950",
    )

    gender_activity = (
        df.groupby(["gender", "activity_type"], as_index=False)["calories_burned"]
        .mean()
        .pivot(index="gender", columns="activity_type", values="calories_burned")
        .round(1)
    )
    act_order = ["HIIT", "Running", "Cycling", "Basketball", "Tennis", "Swimming",
                 "Weight Training", "Dancing", "Walking", "Yoga"]
    gender_activity = gender_activity.reindex(columns=[c for c in act_order if c in gender_activity.columns])

    fig3 = go.Figure(data=go.Heatmap(
        z=gender_activity.values,
        x=gender_activity.columns.tolist(),
        y=gender_activity.index.tolist(),
        colorscale=[[0, "#0d1117"], [0.2, "#0f2a1a"], [0.5, "#1f6feb"], [1, "#3fb950"]],
        text=gender_activity.values.round(1),
        texttemplate="%{text}",
        textfont=dict(size=12, color="#e6edf3"),
        hovertemplate="<b>%{y} · %{x}</b><br>%{z:.1f} kcal avg<extra></extra>",
        colorbar=dict(
            thickness=10,
            tickfont=dict(color=AXIS_COLOR, size=10),
            title=dict(text="kcal", font=dict(color=AXIS_COLOR, size=11)),
        ),
    ))
    apply_dark_theme(fig3, height=240)
    fig3.update_layout(
        title="Avg calories burned: gender × activity type",
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=80, r=60, t=40, b=40),
    )
    chart_wrap(fig3, "gender_activity_heatmap")

    # ── Row 3: Hydration + Duration distribution ───────────────────────────────
    section(
        "Hydration levels and workout duration",
        "Do higher-intensity workouts require more hydration? How long do people actually exercise?",
        color="#58a6ff",
    )

    c4, c5 = st.columns(2)

    with c4:
        hydration_int = (
            df.groupby(["intensity", "activity_type"], as_index=False)["hydration_level"]
            .mean()
            .sort_values("hydration_level", ascending=False)
        )
        hydration_act = (
            df.groupby("activity_type", as_index=False)["hydration_level"]
            .mean()
            .sort_values("hydration_level", ascending=False)
        )
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            y=hydration_act["activity_type"],
            x=hydration_act["hydration_level"],
            orientation="h",
            marker=dict(
                color=[PALETTE[i % len(PALETTE)] for i in range(len(hydration_act))],
                line=dict(width=0),
            ),
            text=hydration_act["hydration_level"].round(3),
            textposition="outside",
            textfont=dict(size=11, color=TEXT_COLOR),
            hovertemplate="<b>%{y}</b><br>%{x:.3f} L<extra></extra>",
        ))
        apply_dark_theme(fig4, height=340)
        fig4.update_layout(
            title="Avg hydration level by activity",
            xaxis_title="Hydration level (L)",
            yaxis_title=None,
            margin=dict(l=120, r=60, t=40, b=40),
            xaxis=dict(range=[2.45, 2.56]),
        )
        chart_wrap(fig4, "hydration_bar")

    with c5:
        sample_dur = df.sample(min(15000, len(df)), random_state=3)
        fig5 = px.box(
            sample_dur,
            x="intensity",
            y="duration_minutes",
            color="intensity",
            color_discrete_map=INTENSITY_COLORS,
            category_orders={"intensity": ["Low", "Medium", "High"]},
        )
        fig5.add_hline(
            y=70, line_dash="dot", line_color="#8b949e", line_width=1,
            annotation_text="Median 70 min",
            annotation_font=dict(size=10, color="#8b949e"),
        )
        apply_dark_theme(fig5, height=340)
        fig5.update_layout(
            title="Workout duration distribution by intensity",
            xaxis_title="Intensity",
            yaxis_title="Duration (minutes)",
            showlegend=False,
        )
        chart_wrap(fig5, "duration_box")

    c4i, c5i = st.columns(2)
    with c4i:
        insight("💡 <strong>Hydration is nearly flat</strong> across activities (~2.5L) — suggesting self-reported hydration may not vary much with actual exertion level in this dataset")
    with c5i:
        insight("💡 <strong>Workout duration is uniform</strong> across intensity levels (median 70 min, range 20–120 min) — participants don't seem to cut short high-intensity sessions")

    # ── Row 4: Fitness level distribution by activity ─────────────────────────
    section(
        "Fitness level across activity types",
        "Do some activities correlate with higher reported fitness? (Note: fitness_level correlates strongly with body weight, r=0.76)",
        color="#d2a8ff",
    )

    fitness_sample = df.sample(min(15000, len(df)), random_state=99)
    fig6 = go.Figure()
    for i, activity in enumerate(sorted(df["activity_type"].unique())):
        sub = fitness_sample[fitness_sample["activity_type"] == activity]["fitness_level"]
        fig6.add_trace(go.Violin(
            x=[activity] * len(sub),
            y=sub,
            name=activity,
            box_visible=True,
            meanline_visible=True,
            fillcolor=PALETTE[i % len(PALETTE)],
            line_color=PALETTE[i % len(PALETTE)],
            opacity=0.6,
            points=False,
            showlegend=False,
        ))
    apply_dark_theme(fig6, height=360)
    fig6.update_layout(
        title="Fitness level distribution by activity type",
        xaxis_title=None,
        yaxis_title="Fitness level",
        xaxis_tickangle=-35,
    )
    chart_wrap(fig6, "fitness_violin")
    insight("⚠️ <strong>Fitness level distributions overlap almost completely</strong> across activities (all centered ~9.5). The dominant predictor is body weight (r=0.76), not activity type.")
