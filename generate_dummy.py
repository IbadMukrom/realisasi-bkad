"""
Script untuk generate data dummy realisasi anggaran BKAD.
Jalankan sekali untuk membuat file data/dummy_data.xlsx
"""
import pandas as pd
import numpy as np
import os

np.random.seed(42)

OPD_NAME = "Badan Keuangan dan Aset Daerah (BKAD)"

# Jenis belanja dengan sub-rincian yang lebih detail
jenis_belanja_list = [
    "Belanja Pegawai",
    "Belanja Barang dan Jasa",
    "Belanja Modal",
    "Belanja Hibah",
    "Belanja Bantuan Sosial",
    "Belanja Tidak Terduga",
    "Belanja Transfer",
]

# Pagu anggaran per jenis belanja (dalam miliar)
pagu_base = {
    "Belanja Pegawai": 45,
    "Belanja Barang dan Jasa": 28,
    "Belanja Modal": 18,
    "Belanja Hibah": 12,
    "Belanja Bantuan Sosial": 5,
    "Belanja Tidak Terduga": 3,
    "Belanja Transfer": 8,
}

rows = []

for tahun in [2024, 2025]:
    for jenis in jenis_belanja_list:
        base = pagu_base[jenis] * 1_000_000_000  # konversi ke rupiah

        # Variasi antar tahun
        if tahun == 2025:
            base *= np.random.uniform(1.03, 1.10)  # naik 3-10%

        # Tambah variasi random
        pagu_jenis = base * np.random.uniform(0.95, 1.05)

        # Generate realisasi per bulan (kumulatif naik)
        bulan_max = 12 if tahun == 2024 else 7  # 2025 sampai Juli
        cumulative = 0

        for bulan in range(1, bulan_max + 1):
            # Realisasi bulanan: proporsi dari pagu dengan variasi
            target_monthly = pagu_jenis / 12
            realisasi_bulanan = target_monthly * np.random.uniform(0.5, 1.3)

            # Awal tahun biasanya lebih rendah
            if bulan <= 2:
                realisasi_bulanan *= 0.5
            elif bulan <= 4:
                realisasi_bulanan *= 0.7
            # Akhir tahun biasanya lebih tinggi (percepatan)
            elif bulan >= 10:
                realisasi_bulanan *= 1.3

            cumulative += realisasi_bulanan

            # Pastikan tidak melebihi pagu
            cumulative = min(cumulative, pagu_jenis * 0.98)

            rows.append({
                "tahun": tahun,
                "nama_opd": OPD_NAME,
                "jenis_belanja": jenis,
                "bulan": bulan,
                "pagu_anggaran": round(pagu_jenis),
                "realisasi": round(cumulative),
            })

df = pd.DataFrame(rows)

# Buat direktori data jika belum ada
os.makedirs("data", exist_ok=True)

# Simpan ke Excel
filepath = "data/dummy_data.xlsx"
df.to_excel(filepath, index=False, sheet_name="Realisasi Anggaran")
print(f"✅ Data dummy BKAD berhasil dibuat: {filepath}")
print(f"   Total baris: {len(df)}")
print(f"   Kolom: {list(df.columns)}")
print(f"   Tahun: {df['tahun'].unique()}")
print(f"   Jenis Belanja: {df['jenis_belanja'].nunique()}")
print(f"\nSample data:")
print(df.head(10).to_string(index=False))
