
# Wellness Tracker — Health Analytics & Data Mining Dashboard

Wellness Tracker is an interactive Streamlit dashboard for exploring health, fitness, lifestyle, and exercise data.  
The app combines descriptive analytics, visual dashboards, workout performance analysis, personalized recommendations, clustering, predictive models, and a lifestyle impact simulator.

The application is available on the next link:
[Fit App](https://fitapp-dataanalysis.streamlit.app)

## Features

### Health Overview
- Key health and fitness indicators
- Population-level summary statistics
- Health condition and BMI distribution
- Activity and calorie trends

### Exercise & Health Impact
- Analysis of relationships between exercise, sleep, stress, BMI, and heart rate
- Correlation and trend-based health insights
- Comparison of health variables across activity groups

### Performance & Lifestyle
- Workout duration analysis
- Calories burned by activity type and intensity
- Activity behavior and lifestyle patterns
- Fitness and performance-related visualizations

### AI & Personalization
- Personalized workout recommendations using KNN
- User segmentation using K-Means clustering
- PCA visualization of health and fitness clusters
- Fitness score prediction using Gradient Boosting Regression
- Stress risk prediction using Gradient Boosting Classification
- Lifestyle impact simulator for comparing current and improved habits

## Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Matplotlib
- Scikit-learn
- SciPy

## Machine Learning Methods

The data mining module includes:

- K-Nearest Neighbors for workout recommendations
- K-Means clustering for user segmentation
- PCA for dimensionality reduction and visualization
- Gradient Boosting Regressor for fitness score prediction
- Gradient Boosting Classifier for stress risk prediction
- Rule-based lifestyle impact simulation

## Project Structure

```text
Fit_App/
│
├── app.py
├── utils.py
├── requirements.txt
├── health_fitness_dataset.csv
│
└── pages/
    ├── p1_executive.py
    ├── p2_health.py
    ├── p3_performance.py
    └── p4_datamining.py
````

## Installation

Clone the repository:

```bash
git clone https://github.com/db075239/Fit_App.git
cd Fit_App
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

## Dataset

The app uses the `health_fitness_dataset.csv` file included in the project.
The dataset contains health, fitness, lifestyle, and workout-related variables such as:

* age
* gender
* BMI
* height and weight
* activity type
* workout duration
* calories burned
* average heart rate
* resting heart rate
* sleep hours
* stress level
* hydration level
* daily steps
* fitness level
* health condition

## Dashboard Navigation

The application contains a landing page and four main modules:

1. Health Overview
2. Exercise & Health Impact
3. Performance & Lifestyle
4. AI & Personalization

Users can navigate using the sidebar or the landing page cards.

## Purpose

This project was developed as a health analytics and data mining dashboard.
The goal is to demonstrate how interactive visualization and machine learning techniques can be used to analyze fitness behavior, identify lifestyle patterns, segment users, and generate personalized insights.

## Notes

The dashboard is intended for exploratory analysis and educational purposes.
Predictions and recommendations are based on patterns in the dataset and should not be interpreted as medical advice.

## Author

David Blazheski


