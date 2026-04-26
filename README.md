# MLOps Pipeline: Sales Value Classification

## Deskripsi Proyek
Repositori ini merupakan implementasi arsitektur Machine Learning Operations (MLOps) end-to-end untuk mendeteksi dan mengklasifikasikan transaksi penjualan menjadi kategori `High_Value` atau `Low_Value`. Pendekatan MLOps yang digunakan pada proyek ini memastikan siklus hidup machine learning berjalan secara otomatis, dapat dilacak (traceable), dan mudah dipantau oleh tim dalam skala produksi.

Proyek ini dirancang secara modular, memisahkan lapisan abstraksi antara tim pengembang (Developer/Tester) dengan tim bisnis (End-User) yang hanya membutuhkan antarmuka visual.

## Arsitektur Sistem
Implementasi pipeline ini meliputi 5 pilar utama MLOps:
1. **Data Preprocessing (Cloud):** Pembersihan dan analisis data eksploratif (EDA) dijalankan menggunakan lingkungan Google Colab agar tidak membebani komputasi lokal.
2. **Model Tracking & Registry:** Terintegrasi dengan DagsHub dan MLflow. Setiap eksperimen, parameter pelatihan (hyperparameter), dan artefak model (file `.pkl`) direkam secara otomatis.
3. **Continuous Integration & Continuous Deployment (CI/CD):** Didukung oleh GitHub Actions. Setiap perubahan kode atau data pada branch `main` akan memicu pelatihan ulang otomatis. Model terbaik kemudian dibungkus sebagai Docker Image dan disimpan pada GitHub Container Registry (GHCR).
4. **Model Serving (Antarmuka Pengguna):** Aplikasi Streamlit di-deploy di Cloud (misal: Streamlit Community Cloud) sebagai antarmuka interaktif yang dapat digunakan secara langsung oleh tim.
5. **Monitoring & Observability:** Metrik prediksi secara dinamis didorong (*push*) dari Streamlit Cloud menuju lingkungan lokal menggunakan **Ngrok Tunneling** dan ditampung oleh **Prometheus Pushgateway**. Metrik kemudian ditarik (*pull*) dan divisualisasikan murni di lingkungan lokal Windows menggunakan **Prometheus** dan **Grafana** (versi Native *standalone*), tanpa memerlukan Docker maupun batasan platform seperti Grafana Cloud.

---

## Struktur Direktori
```text
.
├── data/                       # Direktori penyimpanan raw data (misal: rows.csv)
├── Membangun_model/            # Skrip pengembangan awal dan proses tuning model
├── Monitoring_dan_Logging/     # Source code Streamlit app dan dependensi dashboard
├── notebooks/                  # Notebook Google Colab untuk tahap preprocessing
├── preprocessing/              # Source code pemrosesan ulang (khusus CI/CD)
├── Workflow-CI/                # Skrip pelatihan model otomatis dan integrasi MLflow
├── .github/workflows/          # File konfigurasi GitHub Actions (train.yml)
├── Dockerfile                  # Konfigurasi pembuatan image untuk tahap deployment
├── prometheus.example.yml      # Konfigurasi target Prometheus untuk menarik metrik dari Pushgateway
├── Panduan_Grafana_Prometheus_Lokal.md  # Panduan setup Tunneling Monitoring (Ngrok)
└── README.md                   # Dokumentasi proyek
```

---

## Panduan Instalasi dan Penggunaan Lokal

Instruksi berikut ditujukan untuk menjalankan keseluruhan aplikasi beserta subsistem pemantauannya (opsional) di lingkungan asisten/komputer lokal.

**Prasyarat Sistem:**
* Python versi 3.8 atau yang lebih baru.
* Git terinstal di sistem operasi.

**Langkah-Langkah:**
1. Lakukan kloning repositori menuju komputer lokal:
   ```bash
   git clone https://github.com/RFer7935/MLOps-Experiment.git
   cd MLOps-Experiment
   ```

2. Instal semua dependensi pustaka Python yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```

3. Jalankan aplikasi Streamlit (sebagai antarmuka utama) secara lokal atau akses hasil deploy Streamlit Cloud:
   ```bash
   cd Monitoring_dan_Logging
   streamlit run app.py
   ```
   Akses dasbor pada peramban web di tautan: `http://localhost:8501`.

4. **Aktifkan Pemantauan Metrik MLOps (Ngrok + Pushgateway + Prometheus + Grafana):**
   Mengingat aplikasi Streamlit versi Cloud memiliki *inbound firewall* yang memblokir penarikan (*pull*) metrik dari luar, aplikasi ini telah dirancang untuk MENDORONG (*push*) metrik keluar menuju laptop LOKAL Anda.
   - Silakan rujuk dan praktikkan instruksi menyeluruh pada file **[`Panduan_Grafana_Prometheus_Lokal.md`](Panduan_Grafana_Prometheus_Lokal.md)** untuk menyiapkan jaringan perantara (*tunneling*) dan infrastruktur pemantauan murni di Windows tanpa menggunakan Docker sama sekali.

---

## Informasi Tambahan: Pipeline CI/CD Docker
Sisi *deployment* dari *workflow* GitHub diatur untuk secara otomatis mem-build image Docker dan mendorongnya (push) ke GitHub Container Registry (GHCR) pada tautan `ghcr.io/rfer7935/mlops-experiment`. 

Citra Docker ini difokuskan sebagai bentuk paket lingkungan yang terstandarisasi. Hal ini ditujukan apabila tim infrastruktur berencana melakukan deployment aplikasi pada peladen server Cloud di siklus proyek selanjutnya, sehingga seluruh dependensi tetap identik seperti saat tahap pengujian berlangsung.
