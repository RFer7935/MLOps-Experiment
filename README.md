# Tobacco Smoking Risk Classification — MLOps Project

**Klasifikasi Wilayah Risiko Tinggi Merokok** menggunakan dataset CDC BRFSS Tobacco Use Survey.

## Pipeline
```
Google Colab → GitHub → DockerHub → GitHub Actions → DagsHub → Streamlit
```

## Struktur Project
```
Tobacco_Risk_Classification/
├── data/                        ← Dataset: rows.csv (CDC BRFSS)
├── notebooks/                   ← Google Colab notebook (EDA + Modelling)
├── preprocessing/               ← preprocess.py
├── Membangun_model/             ← modelling.py, modelling_tuning.py
├── Monitoring_dan_Logging/      ← app.py (Streamlit + Prometheus)
├── Workflow-CI/MLProject/       ← MLflow Project + DagsHub logging
├── tests/                       ← pytest unit tests
└── Dockerfile                   ← Docker image untuk deployment
```

## Tools
- **scikit-learn** — Random Forest Classifier, GridSearchCV
- **MLflow + DagsHub** — Experiment tracking & model registry
- **GitHub Actions** — CI/CD pipeline (test → train → deploy)
- **DockerHub** — Container image: `username/tobacco-risk-classification`
- **Streamlit** — Dashboard prediksi interaktif
- **Prometheus** — Monitoring metrics endpoint `:8000/metrics`