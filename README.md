# 📊 Manual Book — Dashboard Realisasi Anggaran BKAD

## Daftar Isi

1. [Pendahuluan](#1-pendahuluan)
2. [Instalasi & Menjalankan Aplikasi](#2-instalasi--menjalankan-aplikasi)
3. [Halaman Dashboard](#3-halaman-dashboard)
4. [Halaman Kelola Data](#4-halaman-kelola-data)
5. [Template Upload Data](#5-template-upload-data)
6. [Struktur Data](#6-struktur-data)
7. [FAQ & Troubleshooting](#7-faq--troubleshooting)

---

## 1. Pendahuluan

Dashboard Realisasi Anggaran BKAD adalah aplikasi web berbasis **Streamlit** yang digunakan untuk:

- **Memvisualisasikan** data realisasi anggaran Badan Keuangan dan Aset Daerah (BKAD)
- **Mengelola** data anggaran (tambah, edit, hapus)
- **Menganalisis** tren dan capaian realisasi per jenis belanja
- **Mengunduh** data dan laporan dalam format CSV

### Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 📊 Dashboard Overview | Metric cards (pagu, realisasi, sisa, persentase) |
| 🎯 Gauge Chart | Visualisasi persentase capaian keseluruhan |
| 📈 Tren Realisasi | Line chart bulanan & triwulanan |
| 📊 Perbandingan Belanja | Bar chart pagu vs realisasi per jenis belanja |
| 🥧 Komposisi Belanja | Donut chart proporsi realisasi |
| 🗓️ Heatmap | Persentase realisasi per jenis belanja per bulan |
| ➕ Input Data | Form tambah data baru |
| ✏️ Edit Data | Tabel interaktif untuk edit data |
| 🗑️ Hapus Data | Hapus data per baris atau bulk |
| 📁 Upload Excel | Upload file Excel untuk mengganti data |
| 📥 Download | Export data ke CSV |

---

## 2. Instalasi & Menjalankan Aplikasi

### Prasyarat

- Python 3.10 atau lebih baru
- pip (package manager Python)

### Langkah Instalasi

```bash
# 1. Buat virtual environment
virtualenv env

# 2. Aktifkan virtual environment
source env/bin/activate        # Linux/Mac
# env\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate data dummy (opsional, untuk demo)
python generate_dummy.py

# 5. Generate template upload (opsional)
python generate_template.py
```

### Menjalankan Aplikasi

```bash
# Pastikan virtual environment aktif
source env/bin/activate

# Jalankan dashboard
streamlit run app.py
```

Aplikasi akan terbuka di browser pada **http://localhost:8501**

---

## 3. Halaman Dashboard

Halaman Dashboard menampilkan visualisasi data realisasi anggaran.

### 3.1 Navigasi

Gunakan **sidebar** (panel kiri) untuk:
- Berpindah antara halaman **📊 Dashboard** dan **📝 Kelola Data**
- Mengatur filter data

### 3.2 Filter Data

Di sidebar, Anda bisa memfilter data berdasarkan:

| Filter | Fungsi |
|--------|--------|
| **📅 Tahun Anggaran** | Pilih tahun yang ingin ditampilkan |
| **💰 Jenis Belanja** | Pilih satu atau lebih jenis belanja (kosongkan untuk menampilkan semua) |

### 3.3 Komponen Dashboard

#### a. Metric Cards (Baris Atas)
Menampilkan 4 indikator utama:
- **💰 Total Pagu Anggaran** — Total pagu seluruh jenis belanja
- **✅ Total Realisasi** — Total realisasi s.d. bulan terakhir
- **📉 Sisa Anggaran** — Selisih pagu dikurangi realisasi
- **📊 Persentase Realisasi** — Capaian dalam persen, dengan badge status:
  - 🟢 **Baik** (≥ 80%)
  - 🟡 **Cukup** (50% - 79%)
  - 🔴 **Rendah** (< 50%)

#### b. Gauge Chart
Menampilkan persentase capaian realisasi keseluruhan dalam bentuk speedometer.

#### c. Tren Realisasi
Pilih tab untuk melihat:
- **📅 Bulanan** — Grafik garis realisasi kumulatif per bulan
- **📊 Triwulanan** — Grafik garis realisasi kumulatif per triwulan

#### d. Perbandingan per Jenis Belanja
Bar chart horizontal menampilkan perbandingan **pagu anggaran** (biru) vs **realisasi** (hijau) untuk setiap jenis belanja, dengan label persentase.

#### e. Komposisi Belanja
Donut chart menampilkan proporsi realisasi masing-masing jenis belanja terhadap total.

#### f. Heatmap
Tabel warna yang menunjukkan persentase realisasi per jenis belanja per bulan:
- 🔴 Merah = realisasi rendah
- 🟡 Kuning = realisasi sedang
- 🟢 Hijau = realisasi tinggi

#### g. Tabel Detail
Tabel ringkasan per jenis belanja dengan kolom: Pagu, Realisasi, Sisa, Persentase.

#### h. Download Data
Dua tombol download di bagian bawah:
- **📥 Download Data (CSV)** — Seluruh data terfilter
- **📥 Download Ringkasan (CSV)** — Ringkasan per jenis belanja

---

## 4. Halaman Kelola Data

Halaman ini memiliki **4 tab** untuk mengelola data:

### 4.1 Tab ➕ Tambah Data

Gunakan form ini untuk menambah data anggaran baru.

**Langkah:**
1. Pilih halaman **📝 Kelola Data** di sidebar
2. Klik tab **➕ Tambah Data**
3. Isi form:
   - **📅 Tahun Anggaran** — Tahun anggaran (2020-2030)
   - **💰 Jenis Belanja** — Pilih dari daftar dropdown
   - **📆 Bulan** — Pilih bulan (1-12)
   - **💰 Pagu Anggaran** — Masukkan pagu dalam Rupiah penuh
   - **✅ Realisasi** — Masukkan realisasi kumulatif dalam Rupiah penuh
4. Klik **💾 Simpan Data Baru**

**Catatan:**
- Tidak bisa menambahkan data duplikat (tahun + jenis belanja + bulan yang sama)
- Pagu Anggaran tidak boleh 0
- Akan muncul peringatan jika realisasi melebihi pagu

### 4.2 Tab ✏️ Edit Data

Gunakan tabel interaktif untuk mengedit data yang sudah ada.

**Langkah:**
1. Klik tab **✏️ Edit Data**
2. (Opsional) Gunakan filter Tahun dan Jenis Belanja untuk mempersempit data
3. **Klik langsung pada sel** yang ingin diedit di tabel
4. Ubah nilai sesuai kebutuhan
5. Klik **💾 Simpan Perubahan**

**Kolom yang bisa diedit:**
- Tahun, Jenis Belanja, Bulan, Pagu Anggaran, Realisasi
- Kolom **Nama OPD** terkunci (tidak bisa diedit)

### 4.3 Tab 🗑️ Hapus Data

Hapus data yang tidak diperlukan.

**Cara 1: Hapus semua data terfilter**
1. Klik tab **🗑️ Hapus Data**
2. Gunakan filter untuk memilih data yang akan dihapus
3. Klik **🗑️ Hapus Semua Data Terfilter**
4. Konfirmasi dengan klik **✅ Ya, Hapus Semua**

**Cara 2: Hapus per baris**
1. Lihat nomor baris (index) di kolom paling kiri tabel
2. Masukkan nomor baris yang ingin dihapus di kotak teks (pisahkan dengan koma)
   - Contoh: `0, 1, 5`
3. Klik **🗑️ Hapus Baris Terpilih**

> ⚠️ **Peringatan:** Data yang dihapus tidak bisa dikembalikan!

### 4.4 Tab 📁 Upload Excel

Upload file Excel untuk mengganti seluruh data yang ada.

**Langkah:**
1. Klik tab **📁 Upload Excel**
2. (Opsional) Klik **📥 Download Template Excel** untuk mendapatkan format yang benar
3. Isi template dengan data Anda
4. Klik **Browse files** dan pilih file Excel
5. Periksa preview data yang ditampilkan
6. Jika format valid (✅), klik **💾 Ganti Data dengan File Ini**

---

## 5. Template Upload Data

### Download Template

Template tersedia di:
- **Di aplikasi:** Tab Upload Excel → klik **📥 Download Template Excel**
- **Di folder proyek:** `data/template_upload.xlsx`

### Isi Template

Template memiliki 2 sheet:

| Sheet | Fungsi |
|-------|--------|
| **Petunjuk Pengisian** | Panduan lengkap cara mengisi data |
| **Data Realisasi** | Sheet untuk mengisi data (ada 3 baris contoh) |

### Cara Mengisi

1. Buka file template di Excel/LibreOffice
2. Baca sheet **Petunjuk Pengisian**
3. Pindah ke sheet **Data Realisasi**
4. **Hapus 3 baris contoh** (baris abu-abu)
5. Isi data Anda mulai dari baris 2
6. Simpan file dengan format **.xlsx**
7. Upload melalui tab Upload Excel di aplikasi

---

## 6. Struktur Data

### Kolom yang Diperlukan

| No | Kolom | Tipe | Keterangan | Contoh |
|----|-------|------|------------|--------|
| 1 | `tahun` | Integer | Tahun anggaran (4 digit) | 2025 |
| 2 | `nama_opd` | Text | Nama lengkap OPD | Badan Keuangan dan Aset Daerah (BKAD) |
| 3 | `jenis_belanja` | Text | Klasifikasi belanja | Belanja Pegawai |
| 4 | `bulan` | Integer (1-12) | Bulan realisasi | 1 |
| 5 | `pagu_anggaran` | Numeric | Pagu dalam Rupiah penuh | 45000000000 |
| 6 | `realisasi` | Numeric | Realisasi kumulatif dalam Rupiah penuh | 2500000000 |

### Aturan Penting

1. **Realisasi bersifat KUMULATIF** — Nilai realisasi bulan ke-n adalah total realisasi dari bulan 1 sampai bulan ke-n
   ```
   Bulan 1: Rp 2.500.000.000 (realisasi bulan 1)
   Bulan 2: Rp 5.200.000.000 (realisasi bulan 1 + bulan 2)
   Bulan 3: Rp 8.100.000.000 (realisasi bulan 1 + 2 + 3)
   ```

2. **Pagu Anggaran bernilai SAMA** untuk semua bulan dalam satu tahun per jenis belanja

3. **Tidak boleh ada duplikat** kombinasi tahun + jenis belanja + bulan

### Jenis Belanja Default

- Belanja Pegawai
- Belanja Barang dan Jasa
- Belanja Modal
- Belanja Hibah
- Belanja Bantuan Sosial
- Belanja Tidak Terduga
- Belanja Transfer

> Anda bisa menambahkan jenis belanja baru melalui form input atau upload Excel.

---

## 7. FAQ & Troubleshooting

### Q: Bagaimana cara mengganti data dummy dengan data asli?
**A:** Ada 2 cara:
1. **Upload Excel:** Buka halaman Kelola Data → tab Upload Excel → upload file data asli Anda
2. **Ganti file:** Timpa file `data/dummy_data.xlsx` dengan file data asli Anda (pastikan kolom sesuai)

### Q: Kenapa dashboard tidak menampilkan data terbaru setelah edit?
**A:** Klik **Rerun** di pojok kanan atas Streamlit, atau refresh browser (F5). Cache akan otomatis ter-clear saat Anda menyimpan perubahan melalui halaman Kelola Data.

### Q: Apakah data aman tersimpan?
**A:** Data disimpan di file Excel lokal (`data/dummy_data.xlsx`). Pastikan untuk melakukan backup secara berkala.

### Q: Bagaimana cara deploy ke internet?
**A:** Ikuti langkah berikut:
1. Push kode ke repository GitHub
2. Login ke [share.streamlit.io](https://share.streamlit.io)
3. Hubungkan repository → pilih `app.py` → Deploy
4. Dashboard akan live di `https://nama-app.streamlit.app`

### Q: Bagaimana jika format Excel saya berbeda?
**A:** Sesuaikan nama kolom di file Excel Anda agar sesuai dengan format yang diperlukan (lihat bagian Struktur Data). Aplikasi akan menolak file yang kolomnya tidak lengkap.

### Q: Aplikasi error saat dijalankan
**A:** Coba langkah berikut:
```bash
# Pastikan virtual environment aktif
source env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Jalankan ulang
streamlit run app.py
```

---

## Struktur File Proyek

```
realisasi-data/
├── app.py                    # Aplikasi utama (Dashboard + Kelola Data)
├── requirements.txt          # Dependencies Python
├── generate_dummy.py         # Script generate data dummy
├── generate_template.py      # Script generate template Excel
├── data/
│   ├── dummy_data.xlsx       # File data utama
│   └── template_upload.xlsx  # Template upload data
├── utils/
│   ├── __init__.py
│   ├── data_loader.py        # Fungsi load & proses data
│   ├── data_manager.py       # Fungsi CRUD (tambah/edit/hapus)
│   └── charts.py             # Fungsi pembuatan chart
├── .streamlit/
│   └── config.toml           # Konfigurasi tema
└── env/                      # Virtual environment
```

---

*Dashboard Realisasi Anggaran BKAD — Dibuat dengan Streamlit & Plotly*
