# 🤖 Guidelines for AI Agents — Realisasi Anggaran BKAD

Dokumen ini berisi pedoman, arsitektur proyek, aturan pengkodean, dan instruksi bagi AI Agent (seperti Antigravity, Cursor, GitHub Copilot, dsb.) saat mengembangkan atau memodifikasi kodebase **Dashboard Realisasi Anggaran BKAD**.

---

## 📌 Ringkasan Proyek

- **Nama Aplikasi**: Dashboard Realisasi Anggaran BKAD
- **Teknologi**: Python 3.10+, Streamlit, Pandas, Plotly, OpenPyXL, gspread
- **Fungsi Utama**: Visualisasi data realisasi anggaran, analisis tren & perbandingan pagu vs realisasi, kelola data (CRUD), sinkronisasi Google Sheets / file lokal (CSV/Excel).

---

## 📁 Struktur Direktori & Komponen Utama

- [app.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/app.py): Entri utama aplikasi Streamlit (UI, navigasi, filter)
- `utils/`: Modul utilitas inti
  - [auth.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/utils/auth.py): Manajemen autentikasi & sesi pengguna
  - [charts.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/utils/charts.py): Pembuatan & kustomisasi grafik Plotly
  - [data_loader.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/utils/data_loader.py): Pemuatan & penyiapan data (Google Sheets / CSV / Excel)
  - [data_manager.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/utils/data_manager.py): Manipulasi data (CRUD, ekspor, validasi)
- `data/`: Penyimpanan data lokal
- [generate_dummy.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/generate_dummy.py): Script pembuat data dummy untuk demo/testing
- [generate_template.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/generate_template.py): Script pembuat template Excel
- [parse_sheet.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/parse_sheet.py): Script pembacaan / parsing data sheet
- [requirements.txt](file:///home/ibad/Documents/proyeku/2026/realisasi-data/requirements.txt): Daftar dependensi Python
- [README.md](file:///home/ibad/Documents/proyeku/2026/realisasi-data/README.md): Dokumentasi dan panduan pengguna

---

## 🛠️ Aturan Pengkodean (Coding Rules & Best Practices)

### 1. **Bahasa & Lokalisasi**
- Interface UI, label chart, pesan error, dan komentar umum menggunakan **Bahasa Indonesia**.
- Format mata uang menggunakan Rupiah (`Rp xxx.xxx.xxx`) dan persentase (`xx.x%`).

### 2. **Streamlit & Caching**
- Gunakan `@st.cache_data` pada fungsi pemuatan data di [data_loader.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/utils/data_loader.py).
- Hindari pemanggilan state global secara langsung tanpa pengecekan `st.session_state`.
- Gunakan `st.rerun()` secara bijak saat memperbarui data agar UI langsung ter-refresh.

### 3. **Keamanan & Konfigurasi**
- **Jangan pernah menyematkan (hardcode)** kredensial (API keys, Service Account JSON, password) langsung di dalam kode.
- Kredensial Google Sheets dan login harus dibaca dari `st.secrets` (rujukan ke `.streamlit/secrets.toml`).

### 4. **Visualisasi Data (Plotly)**
- Semua fungsi grafik ditempatkan di [charts.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/utils/charts.py).
- Pertahankan skema warna yang konsisten untuk menjaga estetika visual dashboard.

### 5. **Pengolahan Data (Pandas & Data Manager)**
- Pastikan kolom tanggal, pagu, dan realisasi dikonversi ke tipe data yang sesuai (`datetime`, `float64`).
- Validasi data saat operasi CRUD di [data_manager.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/utils/data_manager.py) untuk mencegah kesalahan tipe data atau nilai `null`.

---

## 🧪 Perintah Pengembangan & Pengujian (Commands)

```bash
# Aktifkan virtualenv
source env/bin/activate

# Menjalankan aplikasi secara lokal
streamlit run app.py

# Generate data dummy untuk testing
python generate_dummy.py

# Generate template upload Excel
python generate_template.py
```

---

## 🚨 Catatan Penting untuk Agent

1. **Memodifikasi UI**: Sebelum mengubah komponen UI di [app.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/app.py), periksa apakah fungsi utilitas pendukung sudah tersedia di modul `utils/`.
2. **Penanganan Error**: Bungkus panggilan eksternal (Google Sheets API, file I/O) dalam blok `try...except` dan tampilkan pesan error yang informatif via `st.error()`.
3. **Refactoring**: Jika membuat visualisasi grafik baru, tambahkan fungsi kustom tersebut ke [charts.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/utils/charts.py) alih-alih menuliskannya secara inline di [app.py](file:///home/ibad/Documents/proyeku/2026/realisasi-data/app.py).
