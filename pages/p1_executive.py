"""
Dashboard 1 — Executive Health Overview
Key questions answered:
  - Which activities burn the most calories?
  - How does heart rate change across age groups?
  - What is the calorie matrix across activity × intensity?
  - What share of participants have a health condition?
"""
import pandas as pd
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
                Health Overview
            </span><br>
            <span style="font-size:13px;color:#8b949e;letter-spacing:0.3px;">
                Population-level snapshot · 687,701 records · 3,000 participants
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI row ────────────────────────────────────────────────────────────────
    kpi_row([
        {"label": "Avg Daily Steps",      "value": f"{df['daily_steps'].mean():,.0f}",            "color": "#58a6ff"},
        {"label": "Avg Calories Burned",  "value": f"{df['calories_burned'].mean():.1f} kcal",    "color": "#3fb950"},
        {"label": "Avg Exercise HR",      "value": f"{df['avg_heart_rate'].mean():.0f} bpm",       "color": "#f78166"},
        {"label": "Avg Sleep",            "value": f"{df['hours_sleep'].mean():.2f} hrs",          "color": "#d2a8ff"},
        {"label": "Avg Stress",           "value": f"{df['stress_level'].mean():.1f} / 10",        "color": "#ffa657"},
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Calorie ranking + Age × HR line ─────────────────────────────────
    section(
        "Which activity burns the most energy?",
        "Average kilocalories burned per session — HIIT outpaces Yoga by 4×",
        color="#58a6ff",
    )

    c1, c2 = st.columns(2)

    with c1:
        act_summary = (
            df.groupby("activity_type", as_index=False)["calories_burned"]
            .mean()
            .sort_values("calories_burned")
        )
        fig = go.Figure()
        colors = [PALETTE[i % len(PALETTE)] for i in range(len(act_summary))]
        fig.add_trace(go.Bar(
            y=act_summary["activity_type"],
            x=act_summary["calories_burned"],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=act_summary["calories_burned"].round(1),
            textposition="outside",
            textfont=dict(size=11, color=TEXT_COLOR),
            hovertemplate="<b>%{y}</b><br>%{x:.1f} kcal<extra></extra>",
        ))
        apply_dark_theme(fig, height=360)
        fig.update_layout(
            title="Average calories burned per session",
            xaxis_title="Avg kcal",
            yaxis_title=None,
            margin=dict(l=120, r=60, t=40, b=40),
        )
        chart_wrap(fig, "calorie_bar")

    with c2:
        age_hr = (
            df.groupby("age_group", observed=True)["avg_heart_rate"]
            .mean()
            .reset_index()
        )
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=age_hr["age_group"].astype(str),
            y=age_hr["avg_heart_rate"],
            mode="lines+markers+text",
            line=dict(color="#58a6ff", width=2.5),
            marker=dict(size=9, color="#58a6ff", line=dict(color=PLOT_BG, width=2)),
            text=age_hr["avg_heart_rate"].round(0).astype(int).astype(str) + " bpm",
            textposition="top center",
            textfont=dict(size=11, color=TEXT_COLOR),
            hovertemplate="<b>Age %{x}</b><br>%{y:.0f} bpm<extra></extra>",
        ))
        apply_dark_theme(fig2, height=360)
        fig2.update_layout(
            title="Exercise heart rate declines with age",
            xaxis_title="Age group",
            yaxis_title="Avg heart rate (bpm)",
            yaxis=dict(range=[105, 155], gridcolor=GRID_COLOR),
        )
        chart_wrap(fig2, "age_hr_line")

    c1i, c2i = st.columns(2)
    with c1i:
        insight("💡 <strong>HIIT burns 4× more calories</strong> than Yoga (26 vs 6.5 kcal avg per session)")
    with c2i:
        insight("💡 <strong>Heart rate drops ~7 bpm per decade</strong> — from 145 bpm at 18–29 to 116 bpm at 60+")

    # ── Row 2: Intensity heatmap + Health condition breakdown ──────────────────
    section(
        "How does intensity amplify calorie burn?",
        "High-intensity HIIT peaks at 31 kcal — nearly double its own low-intensity variant",
        color="#3fb950",
    )

    c3, c4 = st.columns(2)

    with c3:
        heat_data = (
            df.groupby(["activity_type", "intensity"], as_index=False)["calories_burned"]
            .mean()
            .pivot(index="activity_type", columns="intensity", values="calories_burned")
            .reindex(columns=["Low", "Medium", "High"])
            .sort_values("High", ascending=False)
        )
        fig3 = go.Figure(data=go.Heatmap(
            z=heat_data.values,
            x=["Low", "Medium", "High"],
            y=heat_data.index.tolist(),
            colorscale=[[0, "#0d1117"], [0.3, "#1f6feb"], [0.7, "#f78166"], [1, "#ffa657"]],
            text=heat_data.values.round(1),
            texttemplate="%{text}",
            textfont=dict(size=11),
            hovertemplate="<b>%{y} · %{x}</b><br>%{z:.1f} kcal<extra></extra>",
            showscale=True,
            colorbar=dict(
                thickness=10, len=0.8,
                tickfont=dict(color=AXIS_COLOR, size=10),
                title=dict(text="kcal", font=dict(color=AXIS_COLOR, size=11)),
            ),
        ))
        apply_dark_theme(fig3, height=360)
        fig3.update_layout(
            title="Calorie heatmap: activity × intensity",
            xaxis_title="Intensity",
            yaxis_title=None,
            margin=dict(l=120, r=60, t=40, b=40),
        )
        chart_wrap(fig3, "cal_heatmap")

    with c4:
        cond_counts = df["health_condition"].value_counts().reset_index()
        cond_counts.columns = ["condition", "count"]
        order = ["None", "Hypertension", "Diabetes", "Asthma"]
        cond_counts["condition"] = pd.Categorical(cond_counts["condition"], categories=order, ordered=True)
        cond_counts = cond_counts.sort_values("condition")

        fig4 = go.Figure(data=go.Pie(
            labels=cond_counts["condition"],
            values=cond_counts["count"],
            hole=0.62,
            marker=dict(colors=["#3fb950", "#f78166", "#ffa657", "#58a6ff"],
                        line=dict(color=PLOT_BG, width=2)),
            textinfo="label+percent",
            textfont=dict(size=11, color=TEXT_COLOR),
            hovertemplate="<b>%{label}</b><br>%{value:,} records<br>%{percent}<extra></extra>",
            rotation=90,
        ))
        fig4.add_annotation(
            text="Health<br>Condition",
            x=0.5, y=0.5,
            font=dict(size=12, color=TEXT_COLOR, family=FONT_FAMILY),
            showarrow=False,
        )
        apply_dark_theme(fig4, height=360)
        fig4.update_layout(
            title="Health condition breakdown",
            margin=dict(l=16, r=16, t=40, b=16),
            legend=dict(
                orientation="v", x=1.05, y=0.5,
                font=dict(size=11, color=TEXT_COLOR),
            ),
        )
        chart_wrap(fig4, "health_donut")

    # ── Row 3: BMI × Fitness scatter + Gender bar ──────────────────────────────
    section(
        "Participant body composition profile",
        "BMI distribution and gender breakdown across the study population",
        color="#d2a8ff",
    )

    c5, c6 = st.columns(2)

    with c5:
        bmi_summary = (
            df.groupby("bmi_cat", observed=True, as_index=False)
            .agg(count=("participant_id", "count"), avg_fitness=("fitness_level", "mean"))
        )
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(
            x=bmi_summary["bmi_cat"].astype(str),
            y=bmi_summary["count"],
            marker=dict(
                color=[PALETTE[0], PALETTE[1], PALETTE[2], PALETTE[3]],
                line=dict(width=0),
            ),
            text=bmi_summary["count"].apply(lambda v: f"{v:,.0f}"),
            textposition="outside",
            textfont=dict(size=11, color=TEXT_COLOR),
            hovertemplate="<b>%{x}</b><br>%{y:,} records<extra></extra>",
        ))
        apply_dark_theme(fig5, height=320)
        fig5.update_layout(
            title="Records by BMI category",
            xaxis_title="BMI category",
            yaxis_title="Record count",
        )
        chart_wrap(fig5, "bmi_bar")

    with c6:
        gender_act = (
            df.groupby(["gender", "activity_type"], as_index=False)["calories_burned"]
            .mean()
        )
        fig6 = px.bar(
            gender_act,
            x="activity_type",
            y="calories_burned",
            color="gender",
            barmode="group",
            color_discrete_map={"F": "#58a6ff", "M": "#f78166", "Other": "#3fb950"},
            text_auto=".1f",
        )
        apply_dark_theme(fig6, height=320)
        fig6.update_layout(
            title="Avg calories by gender × activity",
            xaxis_title=None,
            yaxis_title="Avg kcal",
            xaxis_tickangle=-35,
            legend_title_text="Gender",
        )
        fig6.update_traces(textfont_size=9, textposition="outside")
        chart_wrap(fig6, "gender_activity")

    # ── Summary insight row ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    c7, c8, c9 = st.columns(3)
    with c7:
        insight("📌 <strong>High-intensity HIIT</strong> delivers <span class='highlight'>30.9 kcal</span> per session — the top performer across all activity × intensity combinations")
    with c8:
        insight("📌 <strong>Males burn ~21% more</strong> calories per session than females across all activity types")
    with c9:
        insight("📌 <strong>~75% of participants</strong> report no health condition, with Hypertension and Diabetes as the most common comorbidities")
