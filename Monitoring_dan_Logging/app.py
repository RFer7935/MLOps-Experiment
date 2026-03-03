import streamlit as st
import pandas as pd
import joblib
import os
import time
from prometheus_client import (
    Counter, Histogram, Gauge,
    start_http_server, REGISTRY
)

# ─────────────────────────────────────────────
# Prometheus Metrics (cached to avoid duplicate registration on hot-reload)
# ─────────────────────────────────────────────
@st.cache_resource
def create_metrics():
    prediction_total   = Counter("prediction_total",           "Total number of predictions made")
    high_risk_total    = Counter("prediction_high_risk_total", "Total High Risk predictions")
    low_risk_total     = Counter("prediction_low_risk_total",  "Total Low Risk predictions")
    prediction_latency = Histogram("prediction_latency_seconds", "Prediction latency in seconds")
    model_accuracy     = Gauge("model_accuracy",               "Loaded model training accuracy")
    app_requests       = Counter("app_requests_total",         "Total Streamlit app page loads")
    return prediction_total, high_risk_total, low_risk_total, prediction_latency, model_accuracy, app_requests

PREDICTION_TOTAL, HIGH_RISK_TOTAL, LOW_RISK_TOTAL, PREDICTION_LATENCY, MODEL_ACCURACY, APP_REQUESTS = create_metrics()

# Start Prometheus metrics server on port 8000 (only works outside Streamlit Cloud)
@st.cache_resource
def start_metrics_server():
    try:
        start_http_server(8000)
    except OSError:
        pass  # Already started or port unavailable

start_metrics_server()

# ─────────────────────────────────────────────
# Load Model
# ─────────────────────────────────────────────
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "rf_model.pkl"
)

@st.cache_resource
def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

model = load_model()

# ─────────────────────────────────────────────
# App Layout
# ─────────────────────────────────────────────
APP_REQUESTS.inc()
st.set_page_config(page_title="Tobacco Risk Dashboard", layout="wide")
st.title("🚬 Tobacco Smoking Risk Classification Dashboard")
st.caption("Prediksi apakah suatu wilayah/demografi termasuk **High Risk** atau **Low Risk** merokok")

tab1, tab2, tab3 = st.tabs(["🔮 Prediksi", "📊 EDA Dataset", "📈 Model Performance"])

# ─────────────────────────────────────────────
# TAB 1 — Prediksi
# ─────────────────────────────────────────────
with tab1:
    st.subheader("Input Demografi & Lokasi")

    col1, col2, col3 = st.columns(3)
    with col1:
        year        = st.selectbox("Year", options=list(range(2010, 2023)), index=10)
        gender      = st.selectbox("Gender", ["Overall", "Male", "Female"])
        race        = st.selectbox("Race", ["All Races", "White", "Black", "Hispanic", "Asian"])
    with col2:
        age         = st.selectbox("Age Group", ["All Ages", "18-24", "25-44", "45-64", "65+"])
        education   = st.selectbox("Education", ["All Grades", "Less than High School",
                                                   "High School Graduate", "Some College",
                                                   "College Graduate"])
        response    = st.selectbox("Smoking Status (Response)", ["Current", "Former", "Never",
                                                                   "Some Days", "Every Day"])
    with col3:
        location    = st.text_input("Location Abbreviation", value="CA")
        sample_size = st.number_input("Sample Size", min_value=100, max_value=100000, value=5000)
        datasource  = st.selectbox("DataSource", ["BRFSS", "NYTS", "NIS"])
        measure     = st.selectbox("MeasureDesc", ["Smoking Status", "Smoking Frequency",
                                                    "Quit Attempt", "E-cigarette Use"])

    if st.button("🔍 Prediksi Risk Level"):
        if model is None:
            st.error("Model belum tersedia. Jalankan pipeline training terlebih dahulu.")
        else:
            # Simple encoding for demo (same as LabelEncoder ordinal)
            gender_map   = {"Overall": 0, "Female": 1, "Male": 2}
            race_map     = {"All Races": 0, "Asian": 1, "Black": 2, "Hispanic": 3, "White": 4}
            age_map      = {"18-24": 0, "25-44": 1, "45-64": 2, "65+": 3, "All Ages": 4}
            edu_map      = {"All Grades": 0, "College Graduate": 1, "High School Graduate": 2,
                            "Less than High School": 3, "Some College": 4}
            resp_map     = {"Current": 0, "Every Day": 1, "Former": 2, "Never": 3, "Some Days": 4}
            loc_map      = {}  # simplified: hash-based
            ds_map       = {"BRFSS": 0, "NIS": 1, "NYTS": 2}
            meas_map     = {"E-cigarette Use": 0, "Quit Attempt": 1,
                            "Smoking Frequency": 2, "Smoking Status": 3}

            input_data = pd.DataFrame([{
                "YEAR":         year,
                "LocationAbbr": abs(hash(location)) % 60,
                "MeasureDesc":  meas_map.get(measure, 0),
                "DataSource":   ds_map.get(datasource, 0),
                "Response":     resp_map.get(response, 0),
                "Sample_Size":  sample_size,
                "Gender":       gender_map.get(gender, 0),
                "Race":         race_map.get(race, 0),
                "Age":          age_map.get(age, 0),
                "Education":    edu_map.get(education, 0),
            }])

            start_time = time.time()
            prediction = model.predict(input_data)[0]
            probability = model.predict_proba(input_data)[0]
            latency = time.time() - start_time

            # Update Prometheus metrics
            PREDICTION_TOTAL.inc()
            PREDICTION_LATENCY.observe(latency)
            if prediction == 1:
                HIGH_RISK_TOTAL.inc()
            else:
                LOW_RISK_TOTAL.inc()

            # Display result
            if prediction == 1:
                st.error(f"🔴 **HIGH RISK** — Prevalensi merokok tinggi di wilayah/demografi ini")
            else:
                st.success(f"🟢 **LOW RISK** — Prevalensi merokok rendah di wilayah/demografi ini")

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Low Risk Probability",  f"{probability[0]:.2%}")
            col_b.metric("High Risk Probability", f"{probability[1]:.2%}")
            col_c.metric("Latency",               f"{latency*1000:.1f} ms")

# ─────────────────────────────────────────────
# TAB 2 — EDA Dataset
# ─────────────────────────────────────────────
with tab2:
    DATA_PATH = os.path.join(os.path.dirname(__file__),
                             "..", "data", "rows.csv")
    if os.path.exists(DATA_PATH):
        import matplotlib.pyplot as plt
        import seaborn as sns

        df_raw = pd.read_csv(DATA_PATH)
        st.subheader("Preview Dataset")
        st.dataframe(df_raw.head(20), width='stretch')

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Rows",    df_raw.shape[0])
            st.metric("Total Columns", df_raw.shape[1])

        st.subheader("Distribusi Data_Value (Prevalensi Merokok)")
        fig, ax = plt.subplots(figsize=(8, 4))
        df_raw["Data_Value"].dropna().hist(bins=40, ax=ax, color="#E8553E", edgecolor="white")
        ax.axvline(df_raw["Data_Value"].median(), color="navy", linestyle="--",
                   label=f"Median = {df_raw['Data_Value'].median():.1f}%")
        ax.set_xlabel("Data_Value (%)")
        ax.set_ylabel("Frequency")
        ax.legend()
        st.pyplot(fig)

        st.subheader("Rata-rata Prevalensi per Gender")
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        df_raw.groupby("Gender")["Data_Value"].mean().sort_values().plot(
            kind="barh", ax=ax2, color="#3B82F6")
        ax2.set_xlabel("Avg Data_Value (%)")
        st.pyplot(fig2)

        st.subheader("Tren Prevalensi per Tahun")
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        df_raw.groupby("YEAR")["Data_Value"].mean().plot(ax=ax3, marker="o", color="#10B981")
        ax3.set_ylabel("Avg Data_Value (%)")
        ax3.set_xlabel("Year")
        ax3.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig3)
    else:
        st.warning("Dataset rows.csv tidak ditemukan di folder data/. Copy file terlebih dahulu.")

# ─────────────────────────────────────────────
# TAB 3 — Model Performance
# ─────────────────────────────────────────────
with tab3:
    st.subheader("Model Info")
    if model is not None:
        st.success("✅ Model berhasil dimuat")
        st.json({
            "type":         type(model).__name__,
            "n_estimators": model.n_estimators,
            "max_depth":    str(model.max_depth),
            "n_features":   model.n_features_in_,
        })

        st.subheader("Feature Importances")
        feature_names = [
            "YEAR", "LocationAbbr", "MeasureDesc", "DataSource",
            "Response", "Sample_Size", "Gender", "Race", "Age", "Education"
        ]
        importances = pd.Series(model.feature_importances_, index=feature_names)
        fig4, ax4 = plt.subplots(figsize=(7, 4))
        importances.sort_values().plot(kind="barh", ax=ax4, color="#8B5CF6")
        ax4.set_xlabel("Importance")
        st.pyplot(fig4)
    else:
        st.error("Model belum tersedia. Jalankan training pipeline terlebih dahulu.")

    st.subheader("Prometheus Metrics Endpoint")
    st.info("Metrics tersedia di: `http://localhost:8000/metrics`")
    st.code("""
# Metrics yang di-expose:
prediction_total            — total prediksi
prediction_high_risk_total  — total prediksi High Risk
prediction_low_risk_total   — total prediksi Low Risk
prediction_latency_seconds  — histogram latency prediksi
model_accuracy              — akurasi model aktif
app_requests_total          — total request ke dashboard
    """)
