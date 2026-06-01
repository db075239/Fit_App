# ⚡ FitIntel — Health Analytics Platform

A professional, dark-themed Streamlit dashboard analyzing how exercise influences health, fitness, stress, and cardiovascular markers across 687,701 records from 3,000 participants.

---

## Setup

```bash
# 1. Clone / unzip the project
cd fitness_dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Place the dataset in the project root
cp path/to/health_fitness_dataset.csv .

# 4. Run
streamlit run app.py
```

---

## Project Structure

```
fitness_dashboard/
├── app.py                  # Entry point — navigation + global CSS
├── utils.py                # Shared: data loading, Plotly theme, helpers
├── requirements.txt
├── health_fitness_dataset.csv   ← add this file
└── pages/
    ├── __init__.py
    ├── p1_executive.py     # Dashboard 1: Executive Health Overview
    ├── p2_health.py        # Dashboard 2: Exercise & Health Impact
    └── p3_performance.py   # Dashboard 3: Workout Performance & Lifestyle
```

---

## Dashboard Summaries

### Dashboard 1 — Executive Health Overview
**Objective:** Population-level snapshot for executive/strategic audiences.

| Chart | Type | Key finding |
|---|---|---|
| Calories by activity | Horizontal bar | HIIT burns 4× more than Yoga |
| Heart rate vs age | Line + markers | HR drops ~7 bpm per decade |
| Calorie heatmap (activity × intensity) | Annotated heatmap | High-HIIT peaks at 30.9 kcal |
| Health condition breakdown | Donut | ~75% have no condition |
| BMI distribution | Bar | Mostly Normal/Overweight |
| Gender × activity calories | Grouped bar | Males burn ~21% more |

### Dashboard 2 — Exercise & Health Impact
**Objective:** Honest analysis of exercise's effect on stress, BP, sleep, and smoking status.

| Chart | Type | Key finding |
|---|---|---|
| Stress by activity × intensity | Grouped bar | **Null result** — stress barely changes with intensity |
| BP by activity | Bar + error bars + reference lines | All activities cluster near Normal (<120 mmHg) |
| Sleep distribution | Histogram | Centered at 7 hrs (recommended) |
| Stress distribution | Color-coded histogram | Uniform 1–10, no outlier cluster |
| Smoking vs health markers | Grouped bar | <2 bpm difference — snapshot data limitation |
| Sleep vs stress | 2D contour density | No linear relationship |
| Stress by age group | Violin | Identical distributions — age doesn't predict stress |

### Dashboard 3 — Workout Performance & Lifestyle
**Objective:** Efficiency and performance metrics for fitness-focused users.

| Chart | Type | Key finding |
|---|---|---|
| Calorie efficiency (kcal/min) | Polar/radar | HIIT 0.37 vs Yoga 0.09 kcal/min |
| HR zones by activity × intensity | Grouped bar + zone bands | Low=115, Med=133, High=151 bpm — all activities |
| Gender × activity matrix | Full heatmap | Males consistently higher across all activities |
| Hydration by activity | Horizontal bar | Nearly flat — self-reporting limitation |
| Duration by intensity | Box plot | Median 70 min across all intensities |
| Fitness by activity | Violin | Weight (r=0.76) dominates — not activity type |

---

## Design Decisions

### What we DIDN'T do (and why)
- **No fake correlations**: Stress vs daily steps shows r≈0.001. We don't pretend it's meaningful.
- **No misleading fitness_level charts**: fitness_level correlates with weight (r=0.76), not exercise quality. We flag this explicitly.
- **No "relationship" between smoking and health**: Single-session snapshot data can't capture longitudinal smoking effects. We state this.
- **No scatter plots with 687K points**: We sample strategically and use density plots instead.

### Color System
- `#58a6ff` — Blue (informational, step counts, resting metrics)
- `#3fb950` — Green (positive outcomes, sleep, hydration)
- `#f78166` — Coral/Red (high intensity, alerts, stress)
- `#ffa657` — Amber (medium intensity, warnings)
- `#d2a8ff` — Purple (secondary metrics, fitness)
- Background: `#0d1117` sidebar / `#161b22` cards / `#0d1117` page bg

### Typography
- **DM Serif Display** — dashboard titles, KPI values (elegant, authoritative)
- **DM Sans** — all body copy, labels, axis text (clean, modern)

---

## Data Notes

| Field | Range | Notes |
|---|---|---|
| `fitness_level` | 0.02–21.93 | Strongly correlated with weight (r=0.76), not activity |
| `stress_level` | 1–10 | Uniform distribution — no strong predictors found |
| `avg_heart_rate` | ~115–155 bpm | Driven by intensity, declines with age |
| `calories_burned` | 6.5–26 kcal avg | Activity type is the primary driver |
| `resting_heart_rate` | ~70 bpm | Near-uniform across all segments — possible synthetic data artifact |
