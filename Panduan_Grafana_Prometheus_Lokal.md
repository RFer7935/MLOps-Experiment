# Panduan Setup Monitoring Cloud to Lokal (Ngrok Tunneling)

Dokumen ini berisi panduan untuk menyimulasikan lingkungan monitoring di mana **Streamlit di-deploy di platform PaaS/Cloud (seperti Streamlit Community Cloud)**, sementara **Prometheus dan Grafana berjalan murni LOKAL di Windows tanpa Docker**.

Mengingat Streamlit Cloud memblokir port 8000 sehingga Prometheus tidak bisa menarik (*pull*) data, kita menggunakan **Prometheus Pushgateway** dan **Ngrok** agar Streamlit yang MENDORONG (*push*) data menuju laptop lokal Anda.

---

## 1. Setup Pushgateway (Penampung Metrik Lokal)
1. Unduh **Pushgateway** Windows versi terbaru di: [prometheus.io/download/](https://prometheus.io/download/) (pilih file `pushgateway-<VERSI>.windows-amd64.zip`).
2. Ekstrak file Zip tersebut ke folder (contoh: `C:\Pushgateway\`).
3. Buka folder, dan jalankan `pushgateway.exe`. 
   *Pushgateway Anda sekarang aktif menampung metrik di alamat lokal `localhost:9091`.*

---

## 2. Setup Ngrok (Penerowong Internet ke Laptop)
1. Buat akun dan unduh **Ngrok** dari [ngrok.com](https://ngrok.com/).
2. Ekstrak Ngrok dan ikuti instruksi di dashboard mereka untuk menambahkan Authtoken (Langkah ini cuma dilakukan sekali):
   `ngrok config add-authtoken <TOKEN_ANDA>`
3. Hubungkan Pushgateway Anda ke Internet dengan perintah:
   ```bash
   ngrok http 9091
   ```
4. Ngrok akan menampilkan Forwarding URL (Contoh: `https://abcd-123.ngrok-free.app`). 
   **Simpan URL ini**, karena URL ini akan kita pasang di Streamlit. 
   *(Jangan matikan terminal Ngrok ini selagi Streamlit berjalan).*

---

## 3. Konfigurasi Streamlit (Cloud)
Kode Python `app.py` Anda telah dikurasi untuk melakukan *push*. Setiap kali Anda atau dosen merestart Ngrok, Anda harus memperbarui konfigurasi di Streamlit Cloud:

1. Buka file `Monitoring_dan_Logging/app.py`.
2. Cari di sekitar baris ke-25:
   ```python
   NGROK_PUSHGATEWAY_URL = "abcd-123.ngrok-free.app"
   ```
3. Ganti nilainya dengan *Forwarding URL* tanpa `https://` yang baru dari terminal Ngrok.
4. Lakukan `git commit` dan `git push` agar Streamlit Cloud mem-build ulang aplikasinya.

---

## 4. Setup Prometheus (Lokal Windows)
1. Unduh **Prometheus Native** `windows-amd64.zip` dari halaman unduhan yang sama, ekstrak folder.
2. Buka dan ganti isi `prometheus.yml` untuk memantau Pushgateway:
   ```yaml
   global:
     scrape_interval: 15s

   scrape_configs:
     - job_name: "pushgateway-lokal"
       static_configs:
         - targets: ["localhost:9091"]
   ```
3. Jalankan `prometheus.exe --config.file=prometheus.yml`.

---

## 5. Setup & Tautkan Grafana (Lokal Windows)
1. Unduh [Grafana Standalone ZIP](https://grafana.com/grafana/download?platform=windows) lalu ekstrak.
2. Eksekusi `bin/grafana-server.exe`.
3. Buka **`http://localhost:3000`** di browser (User & Pass: `admin`).
4. Klik **Connections > Data Sources > Add data source > Prometheus**.
5. Kolom URL isi dengan: `http://localhost:9090`
6. Lalu klik **Save & Test**.

---

## 6. Membuat Dashboard Visual di Grafana
Jika grafik masih statis atau kosong, ubah pengaturannya mengikuti pola *Prometheus Pushgateway* berikut.

**Panel 1: Total Trafik (Angka Besar)**  
* **Query:** `app_requests_total`
* Tipe: **Stat**
* *Penting:* Scroll panel menu kanan ke opsi `Value options` -> `Calculation` dan pilih **Last \***.

**Panel 2: Distribusi Kelas Penjualan (Pie Chart)**  
* **Query A:** `prediction_high_value_total` *(Legend: High Value)*
* **Query B:** `prediction_low_value_total` *(Legend: Low Value)* 
* Tipe: **Pie chart**
* *Penting:* Di menu `Value options` -> `Calculation`, wajib pilih **Last \***. (Jika tidak diset ke "Last *" grafiknya tidak akan terbentuk).

**Panel 3: Kecepatan Model / Latency (Waktu)**  
* Karena sinyal (Push) dilakukan secara manual setiap terklik, perhitungan rata-rata Histogram seringkali kosong ("No Data") atau patah-patah. Sebaiknya Anda menggunakan metrik nilai tunggal kecepatan terakhir (*Gauge*).
* **Query:** `prediction_last_latency_seconds`
* Tipe: **Time series** (Atau bisa juga **Stat**)
* *Penting:* Pada menu `Value options` -> `Calculation`, pilih opsi **Last \***.

**Panel 4: Akurasi Model Aktif (Meteran Kecepatan)**  
* **Query:** `model_accuracy`
* Tipe: **Gauge**
* *Penting:* Pada menu tipe *Standard Options > Unit* pilih format `Percent (0.0-1.0)` agar angka 0.98 diubah otomatis menjadi 98%.
* Pastikan `Value options` -> Calculation ke **Last \***.

---

## MLOps Dashboard Ready!
Setiap kali tombol *Prediksi* ditekan di website Streamlit Anda yang *online*, sebuah sinyal metrik akan langsung terlempar melewati "terowongan udara" Ngrok ➔ Pushgateway ➔ Ditarik oleh Prometheus ➔ Dimunculkan grafiknya di Grafana Lokal milik Anda!
