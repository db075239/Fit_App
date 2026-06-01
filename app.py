import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(
    page_title="Fitness Analytics · Health Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)
components.html(
    """
    <script>
    window.parent.addEventListener('popstate', function () {
        window.parent.location.reload();
    });
    </script>
    """,
    height=0,
)
page_map = {
    "home": "Home",
    "overview": "Health Overview",
    "impact": "Exercise & Health Impact",
    "performance": "Performance & Lifestyle",
    "ai": "AI & Personalization"
}

url_map = {
    "Home": "home",
    "Health Overview": "overview",
    "Exercise & Health Impact": "impact",
    "Performance & Lifestyle": "performance",
    "AI & Personalization": "ai"
}

page_from_url = st.query_params.get("page", "home")
current_page = page_map.get(page_from_url, "Home")


def go_to(page_name):
    st.query_params["page"] = url_map[page_name]
    st.rerun()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

[data-testid="stSidebarNav"] {
    display: none;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #1e2530;
}

section[data-testid="stSidebar"] * {
    color: #c9d1d9 !important;
}

section[data-testid="stSidebar"] .stRadio label {
    font-size: 14px !important;
    padding: 6px 0 !important;
    letter-spacing: 0.3px;
}

/* Main */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

/* Sidebar branding */
.sidebar-brand {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: #e6edf3;
    margin-bottom: 4px;
    letter-spacing: -0.5px;
}

.sidebar-tagline {
    font-size: 11px;
    color: #6e7681;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 24px;
}

.nav-section {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #6e7681 !important;
    margin: 16px 0 8px 0;
}

/* Home */
.home-hero {
    padding: 70px 20px 35px 20px;
}

.home-title {
    font-family: 'DM Serif Display', serif;
    font-size: 64px;
    color: #e6edf3;
    margin-bottom: 14px;
}

.home-subtitle {
    font-size: 18px;
    color: #8b949e;
    max-width: 850px;
    line-height: 1.7;
}

/* Clickable card buttons */
div[data-testid="stButton"] > button {
    width: 100%;
    min-height: 165px;
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 12px !important;
    padding: 24px 24px !important;
    text-align: left !important;
    color: #e6edf3 !important;
    white-space: pre-line !important;
    transition: 0.25s ease !important;
}

div[data-testid="stButton"] > button:hover {
    border-color: #58a6ff !important;
    background: #1c2128 !important;
    transform: translateY(-3px);
}

div[data-testid="stButton"] > button p {
    font-family: 'DM Serif Display', serif !important;
    font-size: 30px !important;
    line-height: 1.25 !important;
    color: #e6edf3 !important;
}

/* Smaller normal button for sidebar-like use if needed */
.small-button div[data-testid="stButton"] > button {
    min-height: 40px !important;
}

/* Cards and section styles used by pages */
.kpi-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 18px 20px;
}

.kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #8b949e;
    margin-bottom: 6px;
}

.kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 30px;
    color: #e6edf3;
    line-height: 1;
}

.kpi-delta {
    font-size: 12px;
    margin-top: 4px;
    color: #3fb950;
}

.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 26px;
    color: #e6edf3;
    margin: 2rem 0 0.4rem 0;
    border-left: 3px solid #58a6ff;
    padding-left: 14px;
}

.section-sub {
    font-size: 14px;
    color: #8b949e;
    margin-bottom: 1.2rem;
    padding-left: 17px;
}

.insight-pill {
    display: inline-block;
    background: #1c2128;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 10px 16px;
    font-size: 13px;
    color: #c9d1d9;
    margin: 4px 0;
}

.insight-pill strong {
    color: #e6edf3;
}

hr {
    border-color: #21262d !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


from pages import p1_executive
from pages import p2_health
from pages import p3_performance
from pages import p4_datamining


pages = [
    "Home",
    "Health Overview",
    "Exercise & Health Impact",
    "Performance & Lifestyle",
    "AI & Personalization",
]


with st.sidebar:
    st.markdown('<div class="sidebar-brand">⚡ Wellness Tracker</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-tagline">Health Analytics & Workout Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-section">Dashboards</div>', unsafe_allow_html=True)

    selected = st.radio(
        "",
        pages,
        index=pages.index(current_page),
        label_visibility="collapsed",
    )

    if selected != current_page:
        go_to(selected)

    st.markdown("---")
    st.markdown('<div class="nav-section">Filters</div>', unsafe_allow_html=True)


def render_home():
    st.markdown("""
    <div class="home-hero">
        <div class="home-title">⚡ Wellness Tracker</div>
        <div class="home-subtitle">
            Health analytics and workout intelligence platform for exploring fitness behavior, lifestyle patterns, exercise impact, clustering, recommendations, and predictive insights.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(
            "Health Overview\n\nPopulation metrics, KPIs and trends",
            key="card_exec"
        ):
            go_to("Health Overview")

    with col2:
        if st.button(
            "Health Impact\n\nSleep, stress and exercise relationships",
            key="card_health"
        ):
            go_to("Exercise & Health Impact")

    with col3:
        if st.button(
            "Performance\n\nActivity patterns and fitness metrics",
            key="card_perf"
        ):
            go_to("Performance & Lifestyle")

    with col4:
        if st.button(
            "Data Mining\n\nRecommendations and predictive analytics",
            key="card_dm"
        ):
            go_to("AI & Personalization")

    st.markdown("""
    <div class="section-sub">
        Use the sidebar or click one of the cards above to navigate through the analytics pages.
    </div>
    """, unsafe_allow_html=True)



if current_page == "Home":
    render_home()

elif current_page == "Health Overview":
    p1_executive.render()

elif current_page == "Exercise & Health Impact":
    p2_health.render()

elif current_page == "Performance & Lifestyle":
    p3_performance.render()

elif current_page == "AI & Personalization":
    p4_datamining.render()