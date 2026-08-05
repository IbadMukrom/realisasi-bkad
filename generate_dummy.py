"""
Script untuk inisialisasi file template data/dummy_data.xlsx tanpa isi data dummy.
"""
import pandas as pd
import os

OPD_NAME = "Badan Keuangan dan Aset Daerah (BKAD)"
cols = ["tahun", "nama_opd", "penanggungjawab", "kode_rekening", "jenis_belanja", "bulan", "pagu_anggaran", "realisasi"]
df = pd.DataFrame(columns=cols)

os.makedirs("data", exist_ok=True)
filepath = "data/dummy_data.xlsx"
df.to_excel(filepath, index=False, sheet_name="Realisasi Anggaran")
print(f"✅ Template data bersiap: {filepath}")
