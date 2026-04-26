import streamlit as st
import pandas as pd
import joblib
import os
import time
from prometheus_client import (
    Counter, Histogram, Gauge,
    push_to_gateway, REGISTRY
)

# ─────────────────────────────────────────────
# Prometheus Metrics (cached to avoid duplicate registration on hot-reload)
# ─────────────────────────────────────────────
@st.cache_resource
def create_metrics():
    prediction_total   = Counter("prediction_total",           "Total number of predictions made")
    high_value_total   = Counter("prediction_high_value_total", "Total High Value predictions")
    low_value_total    = Counter("prediction_low_value_total",  "Total Low Value predictions")
    prediction_latency = Histogram("prediction_latency_seconds", "Prediction latency in seconds")
    model_accuracy     = Gauge("model_accuracy",               "Loaded model training accuracy")
    app_requests       = Counter("app_requests_total",         "Total Streamlit app page loads")
    return prediction_total, high_value_total, low_value_total, prediction_latency, model_accuracy, app_requests

PREDICTION_TOTAL, HIGH_VALUE_TOTAL, LOW_VALUE_TOTAL, PREDICTION_LATENCY, MODEL_ACCURACY, APP_REQUESTS = create_metrics()

# Konfigurasi URL Pushgateway (Ngrok) untuk Mendorong (Push) Metrik ke Lokal
# PENTING: Ganti URL ini dengan URL Ngrok Anda setiap kali Ngrok direstart! (Tanpa https://)
NGROK_PUSHGATEWAY_URL = " https://craziness-donut-trickster.ngrok-free.dev" 

def push_metrics_to_local():
    try:
        push_to_gateway(NGROK_PUSHGATEWAY_URL, job="sales-model-streamlit-cloud", registry=REGISTRY)
    except Exception as e:
        pass # Abaikan error jika Ngrok mati agar app tidak crash

# ─────────────────────────────────────────────
# Load Model & Accuracy
# ─────────────────────────────────────────────
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "Workflow-CI", "MLProject", "outputs", "rf_model.pkl"
)

@st.cache_resource
def load_model():
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None

model = load_model()

# Set statis untuk simulasi akurasi model dari data testing sebelumnya
MODEL_ACCURACY.set(0.986)

# ─────────────────────────────────────────────
# App Layout
# ─────────────────────────────────────────────
APP_REQUESTS.inc()
push_metrics_to_local()
st.set_page_config(page_title="Sales Value Dashboard", layout="wide")
st.title("📈 Sales Value Classification Dashboard")
st.caption("Prediksi apakah suatu transaksi bernilai **High Value** atau **Low Value**")

tab1, tab2, tab3 = st.tabs(["🔮 Prediksi", "📊 EDA Dataset", "📈 Model Performance"])

# ─────────────────────────────────────────────
# TAB 1 — Prediksi
# ─────────────────────────────────────────────
with tab1:
    st.subheader("Input Data Penjualan")

    col1, col2 = st.columns(2)
    with col1:
        tanggal      = st.date_input("Tanggal Transaksi", value=pd.to_datetime("2022-08-05"))
        jenis_produk = st.selectbox("Jenis Produk", ["Foodpak260", "FoodpakMatte245", "CraftLaminasi290", "Other"])
    with col2:
        jumlah_order = st.number_input("Jumlah Order", min_value=1, max_value=1000000, value=1000)
        harga        = st.number_input("Harga", min_value=1, max_value=1000000, value=1800)

    if st.button("🔍 Prediksi Value Level"):
        if model is None:
            st.error("Model belum tersedia. Jalankan pipeline training terlebih dahulu.")
        else:
            # Simple encoding for demo (same as LabelEncoder)
            # You should ideally save and load local LabelEnoder
            jenis_map = {"CraftLaminasi290": 0, "Foodpak260": 1, "FoodpakMatte245": 2, "Other": 3}
            
            input_data = pd.DataFrame([{
                "Jenis Produk": jenis_map.get(jenis_produk, 3),
                "Jumlah Order": jumlah_order,
                "Harga":        harga,
                "Year":         tanggal.year,
                "Month":        tanggal.month,
                "Day":          tanggal.day
            }])

            start_time = time.time()
            prediction = model.predict(input_data)[0]
            probability = model.predict_proba(input_data)[0]
            latency = time.time() - start_time

            # Update Prometheus metrics
            PREDICTION_TOTAL.inc()
            PREDICTION_LATENCY.observe(latency)
            if prediction == 1:
                HIGH_VALUE_TOTAL.inc()
            else:
                LOW_VALUE_TOTAL.inc()

            # Dorong metrik ke Pushgateway Lokal via Ngrok
            push_metrics_to_local()

            # Display result
            if prediction == 1:
                st.success(f"🟢 **HIGH VALUE** — Prediksi total penjualan tinggi")
            else:
                st.warning(f"🔴 **LOW VALUE** — Prediksi total penjualan rendah")

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Low Value Probability",  f"{probability[0]:.2%}")
            col_b.metric("High Value Probability", f"{probability[1]:.2%}")
            col_c.metric("Latency",               f"{latency*1000:.1f} ms")

# ─────────────────────────────────────────────
# TAB 2 — EDA Dataset
# ─────────────────────────────────────────────
with tab2:
    DATA_PATH = os.path.join(os.path.dirname(__file__),
                             "..", "data", "data_penjualan.csv")
    if os.path.exists(DATA_PATH):
        import matplotlib.pyplot as plt
        import seaborn as sns

        df_raw = pd.read_csv(DATA_PATH, sep=";")
        st.subheader("Preview Dataset Penjualan")
        st.dataframe(df_raw.head(20), width='stretch')

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Rows",    df_raw.shape[0])
            st.metric("Total Columns", df_raw.shape[1])

        st.subheader("Distribusi Total (Sales Value)")
        fig, ax = plt.subplots(figsize=(8, 4))
        df_raw["Total"].dropna().hist(bins=40, ax=ax, color="#3B82F6", edgecolor="white")
        ax.axvline(df_raw["Total"].median(), color="navy", linestyle="--",
                   label=f"Median = {df_raw['Total'].median():.1f}")
        ax.set_xlabel("Total Penjualan")
        ax.set_ylabel("Frequency")
        ax.legend()
        st.pyplot(fig)

        st.subheader("Rata-rata Total per Jenis Produk")
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        df_raw.groupby("Jenis Produk")["Total"].mean().sort_values().plot(
            kind="barh", ax=ax2, color="#10B981")
        ax2.set_xlabel("Avg Total Penjualan")
        st.pyplot(fig2)

    else:
        st.warning("Dataset data_penjualan.csv tidak ditemukan di folder data/. Copy file terlebih dahulu.")

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
            "Jenis Produk", "Jumlah Order", "Harga",
            "Year", "Month", "Day"
        ]
        importances = pd.Series(model.feature_importances_, index=feature_names)
        fig4, ax4 = plt.subplots(figsize=(7, 4))
        importances.sort_values().plot(kind="barh", ax=ax4, color="#10B981")
        ax4.set_xlabel("Importance")
        st.pyplot(fig4)
    else:
        st.error("Model belum tersedia. Jalankan training pipeline terlebih dahulu.")

    st.subheader("Prometheus Metrics Endpoint")
    st.info(f"Metrik di-*push* secara aktif ke: `{NGROK_PUSHGATEWAY_URL}`")
    st.code("""
# Metrics yang di-expose:
prediction_total            — total prediksi
prediction_high_value_total — total prediksi High Value
prediction_low_value_total  — total prediksi Low Value
prediction_latency_seconds  — histogram latency prediksi
model_accuracy              — akurasi model aktif
app_requests_total          — total request ke dashboard
    """)
