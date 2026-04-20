# Panduan Setup Grafana Cloud & Prometheus

Dokumen ini berisi salinan instruksi dari sesi diskusi mengenai cara menghubungkan Streamlit lokal dengan Grafana Cloud menggunakan Prometheus.

## Langkah 1: Jalankan Kurir Prometheus (Lokal Windows/Linux)
Grafana Cloud membutuhkan "kurir" untuk mengirimkan data dari laptop Anda ke server mereka.

1. **Jalankan aplikasi Streamlit Anda:**
   ```bash
   cd Monitoring_dan_Logging
   streamlit run app.py
   ```
2. Buka antarmuka Streamlit (`localhost:8501`) dan **tekan tombol "Prediksi" beberapa kali** agar metrik mulai dihasilkan.
3. Buka terminal baru, pastikan Anda berada di folder yang berisi file `prometheus.yml`, kemudian jalankan Prometheus:
   * **Di Linux/Mac:** `./prometheus --config.file=prometheus.yml`
   * **Di Windows:** `prometheus.exe --config.file=prometheus.yml`
   *(Biarkan terminal ini terus menyala agar pengiriman metrik tidak terputus).*

---

## Langkah 2: Verifikasi Data di Grafana (Menu Explore)
Mari pastikan Grafana Cloud sudah menerima kiriman data dari Prometheus lokal Anda.

1. Buka Dasbor Portal Grafana Cloud Anda di browser (URL: `https://<nama-stack-anda>.grafana.net`).
2. Pada menu panel sebelah kiri, klik ikon **Kompas (Explore)**.
3. Di sudut kiri atas, pastikan **Data Source** yang terpilih adalah sumber Prometheus Cloud Anda (biasanya bernama *grafanacloud-prom* atau sejenisnya).
4. Di kotak bertuliskan *"Enter a PromQL query..."*, ketikkan persis metrik ini:
   ```promql
   prediction_total
   ```
5. Tekan **Enter** (atau klik tombol *Run query* di kanan atas).
6. Jika Anda melihat grafik garis atau angka jumlah klik yang sudah Anda lakukan di Streamlit tadi, artinya koneksi sudah **100% Berhasil!**

---

## Langkah 3: Membuat Dasbor Visual (Dashboard)
Agar presentasi MLOps Anda lengkap, mari buat dasbor utama yang rapi.

1. Di menu Grafana sebelah kiri, klik ikon **Kotak-kotak (Dashboards)**.
2. Klik tombol **New** -> **New dashboard**.
3. Klik tombol biru **+ Add visualization**, lalu pilih Data Source Prometheus Anda.

**Panel 1: Total Trafik (Angka Besar)**
* Di kotak *Query*, ketik: `prediction_total`
* Di menu sisi kanan, ubah tipe *Visualization* dari grafik garis menjadi **Stat**.
* Di menu panel sisi kanan, ubah kotak *Title* menjadi: **"Total Trafik Prediksi"**.
* Klik tombol **Apply** di kanan atas layar.

**Panel 2: Distribusi Kelas Penjualan (Pie Chart)**
* Klik ikon **Add** (logo + di atas) -> **Visualization**.
* Tambahkan 2 Query sekaligus (Klik tombol **+ Add Query**):
  - Query A: `prediction_high_value_total`
  - Query B: `prediction_low_value_total`
* Di sisi kanan, ubah tipe *Visualization* menjadi **Pie Chart**.
* Ubah *Title* menjadi: **"Distribusi Prediksi Penjualan"**.
* Klik **Apply**.

**Panel 3: Kecepatan Model / Latency (Grafik Garis)**
* Klik ikon **Add** -> **Visualization**.
* Di kotak *Query*, masukkan rumus rata-rata kecepatan ini:
  ```promql
  rate(prediction_latency_seconds_sum[1m]) / rate(prediction_latency_seconds_count[1m])
  ```
* Di sisi kanan, ubah *Title* menjadi: **"Kecepatan Proses Model (Detik)"**.
* Klik **Apply**.

**Selesai!**
Terakhir, klik ikon **Save dashboard** (logo Disket di kanan atas) dan beri nama dasbor tersebut: **"MLOps Sales Classification"**. Sekarang Anda memiliki UI Dasbor kelas produksi!
