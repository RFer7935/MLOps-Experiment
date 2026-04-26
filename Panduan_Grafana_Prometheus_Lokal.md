# Panduan Setup Monitoring Cloud to Lokal (Ngrok Tunneling)

Dokumen ini berisi panduan untuk menyimulasikan lingkungan monitoring di mana **Streamlit di-deploy di platform PaaS/Cloud (seperti Streamlit Community Cloud)**, sementara **Prometheus dan Grafana berjalan murni LOKAL di Windows tanpa Docker**.

Mengingat Streamlit Cloud memblokir port 8000 sehingga Prometheus tidak bisa menarik (*pull*) data, kita menggunakan **Prometheus Pushgateway** dan **Ngrok** agar Streamlit yang MENDORONG (*push*) data menuju laptop lokal Anda.

---

## 1. Setup Pushgateway (Penampung Metrik Lokal)
1. Unduh **Pushgateway** Windows versi terbaru di: [prometheus.io/download/](https://prometheus.io/download/) (pilih file `pushgateway-<VERSI>.windows-amd64.zip`).
2. Ekstrak file Zip tersebut ke folder (contoh: `C:\Pushgateway\`).
3. Buka folder hasil ekstrak tersebut. Klik bagian *address bar* (jalur teks alamat putih di bagian atas File Explorer), ketik **`cmd`**, lalu tekan **Enter**.
4. Pada jendela hitam (Command Prompt) yang muncul, ketik perintah ini lalu tekan Enter:
   ```cmd
   pushgateway.exe
   ```
   *Biarkan CMD ini tetap terbuka di background (jangan ditutup). Pushgateway Anda sekarang standby menampung metrik di `localhost:9091`.*

---

## 2. Setup Ngrok (Penerowong Internet ke Laptop)
1. Buat akun gratis di Ngrok: [dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup) dan selesaikan login Anda.
2. Di halaman Dashboard kiri, cari menu **Getting Started** -> **Your Authtoken**. Lalu **Copy** token acak milik Anda.
3. Ekstrak file Zip Ngrok yang sudah diunduh (akan berisi 1 file `ngrok.exe`).
4. Buka folder ekstrakannya, klik *address bar* Windows Explorer (yang membentang putih di atas), ketik **`cmd`**, lalu **Enter**.
5. Di CMD yang barusan terbuka, *Paste* perintah penambahan token Anda. *(Langkah no.5 ini hanya perlu dilakukan 1 kali pertama saja seumur hidup komputer Anda)*:
   ```cmd
   ngrok config add-authtoken <MASUKKAN_VOUCHER_ANDA_DISINI>
   ```
6. Jika profil sukses dikonfigurasi, jalankan fitur penerowongan *port-forwarding* (membuka aplikasi ke internet):
   ```cmd
   ngrok http 9091
   ```
7. Ngrok akan menampilkan jendela status dengan baris hijau/biru. Perhatikan baris **Forwarding**. Kopi URL-nya (Contoh: `https://abcd-123.ngrok-free.app`). 
   *Simpan URL ini untuk dipasang di parameter Streamlit. Dan ingat, biarkan jendela terminal Ngrok ini berjalan selama Streamlit masih diakses!*

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
3. Buka folder ekstrakan **Prometheus** tersebut (yang menyimpan `prometheus.exe` dan `prometheus.yml`).
4. Klik area baris alamat atau *address bar* Windows Explorer di paling atas, ketik **`cmd`**, lalu **Enter**.
5. CMD baru akan terbuka di layar Anda. Ketikkan baris perintah berikut sambil teliti huruf kapitalnya:
   ```cmd
   prometheus.exe --config.file=prometheus.yml
   ```
   *Biarkan CMD ini terus berjalan berkedip-kedip di background Anda.*

---

## 5. Setup & Tautkan Grafana (Lokal Windows)
1. Unduh [Grafana Standalone ZIP](https://grafana.com/grafana/download?platform=windows), lalu *Extract All* file di folder baru.
2. Buka folder baru dari Grafana yang diekstrak tadi, masuklah ke dalam sub-folder bernama **`bin`**.
3. Sama seperti program yang lain di layar ini, klik daerah *address bar* Explorer kosong di sebelah nama folder Anda (paling atas putih). Ketikkan `cmd`, lalu Enter.
4. Jendela Command Prompt baru akan muncul (ingat, Terminal ini harus digarisbawahi jalurnya **berakhir pada ...\bin**). Ketik:
   ```cmd
   grafana-server.exe
   ```
5. Tunggu tulisan log bermunculan yang mencerminkan Grafana server `started!`.
6. Bukalah Tab Browser baru (Chrome / Edge / Firefox) dan jalankan URL Default: **`http://localhost:3000`**
7. Anda akan melihat halaman Login. Gunakan default: `admin` dan pass: `admin` (Anda bisa memperbaruinya nanti).
8. Klik icon Menu Navigasi **Connections** (atau Configuration) > **Data Sources** > **Add data source** > pilih logo **Prometheus**.
9. Ada sebuah form besar, di bawah segmen HTTP, pada baris "URL / Server URL" isi secara akurat dengan alamat Prometheus Anda: `http://localhost:9090`
10. Gulung kursor ke bawah pol, lalu klik tombol biru **Save & Test**. (Pastikan centang hijau "Data source is working" muncul).

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
