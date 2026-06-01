import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, RobustScaler
from sklearn.neighbors import NearestNeighbors, LocalOutlierFactor
from sklearn.cluster import KMeans, DBSCAN, SpectralClustering
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.ensemble import GradientBoostingClassifier,GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

from utils import (
    PALETTE, INTENSITY_COLORS, PLOT_BG, PAPER_BG, GRID_COLOR, TEXT_COLOR,
    AXIS_COLOR, FONT_FAMILY, apply_dark_theme, load_data, sidebar_filters,
    section, chart_wrap, insight, kpi_row,
)

#Clustering models

@st.cache_resource
def train_knn_model():
    """Train KNN recommender on historical data."""
    data = pd.read_csv("health_fitness_dataset.csv")
    features = ['age', 'gender', 'height_cm', 'weight_kg', 'bmi', 'stress_level', 'duration_minutes']
    target = 'activity_type'
    data_filtered = data[features + [target]].dropna()

    le_gender = LabelEncoder()
    data_filtered['gender_encoded'] = le_gender.fit_transform(data_filtered['gender'])

    X = data_filtered[['age', 'gender_encoded', 'height_cm', 'weight_kg', 'bmi', 'stress_level', 'duration_minutes']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    knn = NearestNeighbors(n_neighbors=10)
    knn.fit(X_scaled)

    return knn, scaler, le_gender, data_filtered, target


@st.cache_resource
def train_clustering_model():
    """Train K-means clustering on latest health data."""
    data = pd.read_csv("health_fitness_dataset.csv")
    data['date'] = pd.to_datetime(data['date'])
    latest_entries = data.sort_values('date').groupby('participant_id').tail(1).reset_index(drop=True)

    features = [
        'age', 'bmi', 'duration_minutes', 'calories_burned',
        'avg_heart_rate', 'hours_sleep', 'stress_level',
        'daily_steps', 'hydration_level', 'fitness_level'
    ]
    X = latest_entries[features].dropna()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    result_df = latest_entries.loc[X.index].copy()
    result_df['cluster'] = clusters
    result_df['PCA1'] = X_pca[:, 0]
    result_df['PCA2'] = X_pca[:, 1]

    cluster_summary = result_df.groupby('cluster')[features].mean()

    return result_df, cluster_summary, features


def recommend_workouts(user_input, knn, scaler, le_gender, data_filtered, target, top_n=5):
    user_input_encoded = user_input.copy()
    user_input_encoded[1] = le_gender.transform([user_input[1]])[0]
    user_scaled = scaler.transform([user_input_encoded])
    distances, indices = knn.kneighbors(user_scaled)
    activities = data_filtered.iloc[indices[0]][target].values
    most_common = Counter(activities).most_common(top_n)
    return [activity for activity, _ in most_common]


# Classification models


@st.cache_resource
def train_stress_classifier():
    """Predict high stress level (>median)."""
    data = pd.read_csv("health_fitness_dataset.csv")
    
    user_stats = data.groupby('participant_id').agg({
        'age': 'first',
        'bmi': 'mean',
        'hours_sleep': 'mean',
        'daily_steps': 'mean',
        'duration_minutes': 'mean',
        'avg_heart_rate': 'mean',
        'hydration_level': 'mean',
        'stress_level': 'mean',
        'calories_burned': 'mean',
    }).reset_index()
    
    user_stats = user_stats.dropna()
    
    # Target: High stress (>median)
    stress_threshold = user_stats['stress_level'].median()
    user_stats['high_stress'] = (user_stats['stress_level'] > stress_threshold).astype(int)
    
    feature_cols = ['age', 'bmi', 'hours_sleep', 'daily_steps', 'duration_minutes',
                    'avg_heart_rate', 'hydration_level', 'calories_burned']
    
    X = user_stats[feature_cols]
    y = user_stats['high_stress']
    
    # Only proceed if we have both classes
    if y.nunique() < 2:
        # Fallback: if all same class, just return a dummy classifier
        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(X)
        from sklearn.dummy import DummyClassifier
        clf = DummyClassifier(strategy='most_frequent')
        clf.fit(X_scaled, y)
        return clf, scaler, feature_cols
    
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    
    clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, 
                                     max_depth=5, random_state=42, verbose=0)
    clf.fit(X_scaled, y)
    
    return clf, scaler, feature_cols

@st.cache_resource
def train_fitness_score_regressor():
    data = pd.read_csv("health_fitness_dataset.csv")

    user_stats = data.groupby("participant_id").agg({
        "age": "first",
        "bmi": "mean",
        "resting_heart_rate": "mean",
        "blood_pressure_systolic": "mean",
        "daily_steps": "mean",
        "hours_sleep": "mean",
        "stress_level": "mean",
        "hydration_level": "mean",
        "duration_minutes": "mean",
        "calories_burned": "mean",
        "avg_heart_rate": "mean",
        "fitness_level": "mean",
    }).reset_index()

    user_stats["workout_frequency"] = data.groupby("participant_id").size().values
    user_stats["activity_diversity"] = data.groupby("participant_id")["activity_type"].nunique().values

    user_stats = user_stats.dropna()

    feature_cols = [
        "age", "bmi", "resting_heart_rate", "blood_pressure_systolic",
        "daily_steps", "hours_sleep", "stress_level", "hydration_level",
        "duration_minutes", "calories_burned", "avg_heart_rate",
        "workout_frequency", "activity_diversity"
    ]

    X = user_stats[feature_cols]
    y = user_stats["fitness_level"]

    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)

    model = GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.08,
        max_depth=4,
        random_state=42
    )

    model.fit(X_scaled, y)

    importance = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": model.feature_importances_
    }).sort_values("Importance", ascending=False)

    return model, scaler, feature_cols, importance

st.markdown("""
<style>
div[data-testid="stButton"] > button {
    min-height: 38px !important;
    min-width: 38px !important;
}
</style>
""", unsafe_allow_html=True) 
def render():
    st.markdown(
        """
        <div style="margin-bottom:1.4rem">
            <span style="font-family:'DM Serif Display',serif;font-size:32px;color:#e6edf3;">
                Advanced Machine Learning &amp; Insights
            </span><br>
            <span style="font-size:13px;color:#8b949e;letter-spacing:0.3px;">
                Personalized recommendations · Clustering analysis · Predictive insights
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Create tabs for different analyses
    tab1, tab2, tab3= st.tabs([
        " Recommendations",
        " Clustering",
        " Predictions",
    ])

    # Tab 1: Personalized Recommendations
    with tab1:
        section(
            "Get personalized workout recommendations",
            "Find activities that match users with your health profile ",
            color="#58a6ff",
        )

        knn, scaler, le_gender, data_filtered, target = train_knn_model()

        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.slider("Age", 18, 64, 30, key="age_rec")
        with col2:
            gender = st.selectbox("Gender", options=["M", "F"], key="gender_rec")
        with col3:
            height = st.slider("Height (cm)", 140, 220, 175, key="height_rec")

        col4, col5, col6 = st.columns(3)
        with col4:
            weight = st.slider("Weight (kg)", 40, 150, 70, key="weight_rec")
        with col5:
            bmi = weight / ((height / 100) ** 2)
            st.metric("BMI", f"{bmi:.1f}")
        with col6:
            stress = st.slider("Stress Level", 1, 10, 5, key="stress_rec")

        duration = st.slider("Preferred Duration (min)", 15, 120, 45, key="duration_rec")

        if st.button("🔍 Find My Recommendations", use_container_width=True, key="rec_btn"):
            user_profile = [age, gender, height, weight, bmi, stress, duration]  
            
            recs = recommend_workouts(user_profile, knn, scaler, le_gender, data_filtered, target, top_n=5)


            st.markdown("Top 5 Recommended Activities:")
            col_recs = st.columns(5)
            for i, (col, rec) in enumerate(zip(col_recs, recs)):
                col.metric(f"#{i+1}", rec)
                

            insight(
            f"<strong>Based on your profile:</strong> Users similar to you (age {age}, {gender}, {height}cm, {weight}kg) "
            f"most frequently do <span class='highlight'>{recs[0]}</span>."
            )

        st.divider()
    
    # Tab 2: Clustering analysis
    with tab2:
        section(
            "Discover your health & fitness cluster",
            "See how you compare to similar users and get tailored insights",
            color="#3fb950",
        )
        result_df, cluster_summary, features = train_clustering_model()

        # PCA visualization
        cluster_colors = {0: "#58a6ff", 1: "#3fb950", 2: "#f78166", 3: "#d2a8ff"}
        cluster_info = {
            0: {
                "name": "Young, High-Activity Users",
                "description": "Active individuals with long workouts, high calorie burn and elevated heart rates. May benefit from performance-focused programs and recovery support."
            },
            1: {
                "name": "Older, Consistent Exercisers",
                "description": "Older users maintaining long, steady workouts with good hydration and sleep. Ideal for endurance-focused and age-adapted fitness plans."
            },
            2: {
                "name": "Older, Low-Activity Group",
                "description": "Low-intensity participants with short sessions and low calorie burn. Ideal for beginner routines and motivational coaching."
            },
            3: {
                "name": "Young, Inefficient Exercisers",
                "description": "Younger users with high heart rates despite low workout output, showing excessive effort. They need structured, guided training and stress management support."
            },
        }
        
        result_df['cluster_name'] = result_df['cluster'].map({k: v["name"] for k, v in cluster_info.items()})

        fig_pca = px.scatter(
            result_df,
            x="PCA1",
            y="PCA2",
            color="cluster_name",
            color_discrete_map={v["name"]: cluster_colors[k] for k, v in cluster_info.items()},
            hover_data=["age", "bmi", "avg_heart_rate", "hours_sleep", "stress_level"],
            title="User Segmentation in 2D (PCA)",
            labels={"PCA1": "PC1 (Primary Variance)", "PCA2": "PC2 (Secondary Variance)"},
        )
        apply_dark_theme(fig_pca, height=420)
        fig_pca.update_traces(marker=dict(size=7, opacity=0.7))
        chart_wrap(fig_pca, "pca_scatter")

        # Cluster summary metrics
        st.markdown("**Cluster Profiles & Recommendations:**")
        for cluster_id in sorted(result_df['cluster'].unique()):
            cluster_label = cluster_info[cluster_id]["name"]
            cluster_desc = cluster_info[cluster_id]["description"]
            cluster_size = len(result_df[result_df['cluster'] == cluster_id])
            
            # Get summary stats for the cluster
            avg_age = cluster_summary.loc[cluster_id, 'age']
            avg_bmi = cluster_summary.loc[cluster_id, 'bmi']
            avg_duration = cluster_summary.loc[cluster_id, 'duration_minutes']
            avg_calories = cluster_summary.loc[cluster_id, 'calories_burned']
            avg_hr = cluster_summary.loc[cluster_id, 'avg_heart_rate']
            avg_sleep = cluster_summary.loc[cluster_id, 'hours_sleep']
            avg_stress = cluster_summary.loc[cluster_id, 'stress_level']
            avg_steps = cluster_summary.loc[cluster_id, 'daily_steps']
            avg_hydration = cluster_summary.loc[cluster_id, 'hydration_level']

            # Display cluster header
            st.markdown(f"### {cluster_label} ({cluster_size} users)")
            st.markdown(f"_{cluster_desc}_")

            # Display metrics in columns
            metric_cols = st.columns(6)
            with metric_cols[0]:
                st.metric("Avg Age", f"{avg_age:.0f} yrs")
            with metric_cols[1]:
                st.metric("Avg HR", f"{avg_hr:.0f} bpm")
            with metric_cols[2]:
                st.metric("Avg Sleep", f"{avg_sleep:.1f} hrs")
            with metric_cols[3]:
                st.metric("Avg Stress", f"{avg_stress:.1f}/10")
            with metric_cols[4]:
                st.metric("Avg Duration", f"{avg_duration:.0f} min")
            with metric_cols[5]:
                st.metric("Avg Steps", f"{avg_steps:,.0f}")
         
            st.divider()
    # TAB 3: Predictions 
    with tab3:
        section(
            "Predict fitness and stress outcomes. Have a glimpse into improved lifestyle.",
            "Machine learning models based on your profile and habits",
            color="#3fb950",
        )
        pred_col1, pred_col2 = st.columns(2)

        with pred_col1:
            st.markdown("### Fitness Score Prediction")
            fitness_model, fitness_scaler, fitness_features, fitness_importance = train_fitness_score_regressor()

            age = st.slider("Age", 18, 64, 40, key="fit_score_age")
            bmi = st.slider("BMI", 15.0, 40.0, 25.0, key="fit_score_bmi")
            steps = st.slider("Daily Steps", 2000, 20000, 9000, key="fit_score_steps")
            sleep = st.slider("Sleep Hours", 4.0, 10.0, 7.0, key="fit_score_sleep")
            hydration = st.slider("Hydration Level (L)", 0.5, 5.0, 2.0, key="fit_score_hydration")
            stress = st.slider("Stress Level", 1.0, 10.0, 5.0, key="fit_score_stress")
            duration = st.slider("Workout Duration", 15, 120, 45, key="fit_score_duration")
            frequency = st.slider("Workouts / Month", 4, 30, 16, key="fit_score_freq")

            if st.button("Predict Fitness Score", key="predict_fitness_score"):
                profile = np.array([[
                    age, bmi, 75.0, 125.0,
                    steps, sleep, stress, hydration,
                    duration, 350.0, 120.0,
                    frequency, 4.0
                ]])

                profile_scaled = fitness_scaler.transform(profile)
                fitness_score = fitness_model.predict(profile_scaled)[0]

                st.success(f"Predicted Fitness Score: **{fitness_score:.1f} / 100**")

                st.markdown("**Most important factors:**")
                st.dataframe(
                    fitness_importance.head(5),
                    use_container_width=True,
                    hide_index=True
                )

        with pred_col2:
            st.markdown("###  Stress Level Prediction")
            
            stress_clf, stress_scaler, stress_features = train_stress_classifier()

            stress_age = st.slider("Age", 18, 64, 40, key="stress_age")
            stress_bmi = st.slider("BMI", 15.0, 40.0, 25.0, key="stress_bmi")
            stress_steps = st.slider("Daily Steps", 2000, 20000, 10000, key="stress_steps")
            stress_sleep = st.slider("Sleep Hours", 4.0, 10.0, 7.0, key="stress_sleep")
            stress_hydration = st.slider("Hydration Level (L)", 0.5, 5.0, 2.0, key="stress_hydration")
            stress_hr = st.slider("Avg Heart Rate", 60, 160, 100, key="stress_hr")
            stress_duration = st.slider("Workout Duration (min)", 15, 120, 45, key="stress_duration")
            stress_calories = st.slider("Calories Burned", 100, 1000, 350, key="stress_calories")

            if st.button("Predict Stress Level", key="stress_pred_btn"):
                user_stress_profile = np.array([[
                    stress_age,
                    stress_bmi,
                    stress_sleep,
                    stress_steps,
                    stress_duration,
                    stress_hr,
                    stress_hydration,
                    stress_calories
                ]])

                user_stress_scaled = stress_scaler.transform(user_stress_profile)
                stress_prob = stress_clf.predict_proba(user_stress_scaled)[0]
                
                if stress_prob[1] > 0.6:
                    st.warning(f"**High Stress Risk**: {stress_prob[1]*100:.1f}%")
                else:
                    st.info(f"**Stress Level**: {stress_prob[1]*100:.1f}% (Low Risk)")
                    
                
        st.markdown("---")

        st.markdown("###  Lifestyle Impact Simulator")
        st.caption("Compare current habits with an improved lifestyle scenario.")

        def calculate_lifestyle_score(steps, sleep, stress, hydration, duration, frequency):
            steps_score = min(steps / 12000, 1) * 25
            sleep_score = max(0, 1 - abs(sleep - 8) / 4) * 20
            stress_score = max(0, (10 - stress) / 9) * 20
            hydration_score = min(hydration / 3, 1) * 15
            workout_score = min(duration / 60, 1) * 10
            frequency_score = min(frequency / 20, 1) * 10

            return steps_score + sleep_score + stress_score + hydration_score + workout_score + frequency_score


        sim_col1, sim_col2 = st.columns(2)

        with sim_col1:
            st.markdown("#### Current Lifestyle")

            current_steps = st.slider("Current Daily Steps", 2000, 20000, 6000, key="current_steps")
            current_sleep = st.slider("Current Sleep", 4.0, 10.0, 6.0, key="current_sleep")
            current_stress = st.slider("Current Stress", 1.0, 10.0, 7.0, key="current_stress")
            current_hydration = st.slider("Current Hydration (L)", 0.5, 5.0, 1.5, key="current_hydration")
            current_duration = st.slider("Current Workout Duration", 15, 120, 30, key="current_duration")
            current_frequency = st.slider("Current Workouts / Month", 4, 30, 8, key="current_frequency")

        with sim_col2:
            st.markdown("#### Improved Lifestyle")

            improved_steps = st.slider("Improved Daily Steps", 2000, 20000, 10000, key="improved_steps")
            improved_sleep = st.slider("Improved Sleep", 4.0, 10.0, 8.0, key="improved_sleep")
            improved_stress = st.slider("Improved Stress", 1.0, 10.0, 4.0, key="improved_stress")
            improved_hydration = st.slider("Improved Hydration (L)", 0.5, 5.0, 2.5, key="improved_hydration")
            improved_duration = st.slider("Improved Workout Duration", 15, 120, 60, key="improved_duration")
            improved_frequency = st.slider("Improved Workouts / Month", 4, 30, 18, key="improved_frequency")

        if st.button("Run Lifestyle Simulation", key="lifestyle_sim_btn"):

            current_score = calculate_lifestyle_score(
                current_steps,
                current_sleep,
                current_stress,
                current_hydration,
                current_duration,
                current_frequency
            )

            improved_score = calculate_lifestyle_score(
                improved_steps,
                improved_sleep,
                improved_stress,
                improved_hydration,
                improved_duration,
                improved_frequency
            )

            improvement = improved_score - current_score

            current_stress_risk = max(0, min(100, current_stress * 10 - current_sleep * 3 - current_hydration * 2))
            improved_stress_risk = max(0, min(100, improved_stress * 10 - improved_sleep * 3 - improved_hydration * 2))

            stress_reduction = current_stress_risk - improved_stress_risk

            current_calories = current_duration * 7 + current_frequency * 8
            improved_calories = improved_duration * 7 + improved_frequency * 8

            calories_gain = improved_calories - current_calories

            results_df = pd.DataFrame({
                "Metric": [
                    "Lifestyle Score",
                    "Stress Risk",
                    "Estimated Calories Impact"
                ],
                "Current": [
                    f"{current_score:.1f} / 100",
                    f"{current_stress_risk:.1f}%",
                    f"{current_calories:.0f} kcal"
                ],
                "Improved": [
                    f"{improved_score:.1f} / 100",
                    f"{improved_stress_risk:.1f}%",
                    f"{improved_calories:.0f} kcal"
                ],
                "Change": [
                    f"+{improvement:.1f}",
                    f"-{stress_reduction:.1f}%",
                    f"+{calories_gain:.0f} kcal"
                ]
            })

            st.dataframe(
                results_df,
                use_container_width=True,
                hide_index=True
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Lifestyle Score", f"{improved_score:.1f}", f"+{improvement:.1f}")

            with col2:
                st.metric("Stress Risk", f"{improved_stress_risk:.1f}%", f"-{stress_reduction:.1f}%")

            with col3:
                st.metric("Calories Impact", f"{improved_calories:.0f} kcal", f"+{calories_gain:.0f} kcal")

            if improvement >= 20:
                st.success("Strong lifestyle improvement detected. Better sleep, hydration, activity, and lower stress create a healthier profile.")
            elif improvement >= 8:
                st.info("Moderate improvement detected. The lifestyle changes are likely beneficial.")
            else:
                st.warning("Only a small improvement is detected. Try increasing activity, sleep, hydration, or lowering stress.")

    
