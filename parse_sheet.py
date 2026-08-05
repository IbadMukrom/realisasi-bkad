"""
Script pengolahan data asli BKAD dari Google Sheets ke file data/dummy_data.xlsx
"""
import pandas as pd
import numpy as np
import io
import os

csv_file = "/home/ibad/.gemini/antigravity-ide/brain/49c734f6-065b-4933-8d17-a180eb9b7c83/.system_generated/steps/449/content.md"

with open(csv_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

data_lines = []
start = False
for line in lines:
    if "Kode Rekening" in line:
        start = True
    if start:
        data_lines.append(line)

csv_data = "".join(data_lines)
df_raw = pd.read_csv(io.StringIO(csv_data))
df_raw.columns = df_raw.columns.str.strip()

def clean_num(val):
    if pd.isna(val):
        return 0.0
    s = str(val).replace('"', '').replace(' ', '').replace('-', '0').replace(',', '')
    try:
        return float(s)
    except:
        return 0.0

months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

for col in ["Pagu"] + months + ["JUMLAH", "SISA ANGGARAN"]:
    if col in df_raw.columns:
        df_raw[col] = df_raw[col].apply(clean_num)

df_raw["PENANGGUNGJAWAB"] = df_raw["PENANGGUNGJAWAB"].fillna("").astype(str).str.strip()
df_raw["Uraian"] = df_raw["Uraian"].fillna("").astype(str).str.strip()
df_raw["Kode Rekening"] = df_raw["Kode Rekening"].fillna("").astype(str).str.strip()

# Map penanggung jawab shorthand to full readable names
pj_map = {
    "Sekretariat": "Sekretariat",
    "Bidang Anggaran": "Bidang Anggaran",
    "Bidang Perbend": "Bidang Perbendaharaan",
    "Bidang Akpel": "Bidang Akuntansi & Pelaporan",
    "Bidang Pengelolaan BMD": "Bidang Pengelolaan BMD",
}

# Standardize penanggungjawab
def fix_pj(pj_str, uraian):
    if pj_str in pj_map:
        return pj_map[pj_str]
    elif "Sekretariat" in pj_str:
        return "Sekretariat"
    elif "Anggaran" in pj_str:
        return "Bidang Anggaran"
    elif "Perbend" in pj_str:
        return "Bidang Perbendaharaan"
    elif "Akpel" in pj_str or "Akuntansi" in pj_str:
        return "Bidang Akuntansi & Pelaporan"
    elif "BMD" in pj_str:
        return "Bidang Pengelolaan BMD"
    else:
        return "Sekretariat"  # Default fallback

# Sub-kegiatan level check (kode ending with 4 digits like 0001, 0002)
rows_list = []

for idx, row in df_raw.iterrows():
    kode = str(row["Kode Rekening"]).strip()
    uraian = str(row["Uraian"]).strip()
    pj_raw = str(row["PENANGGUNGJAWAB"]).strip()
    pagu = float(row["Pagu"])

    # Skip total header (5.02 KEUANGAN) and program headers if pagu is zero
    if not kode or pagu <= 0:
        continue

    # Only process rows that have actual sub-kegiatan code (or non-empty penanggungjawab)
    # Check if kode matches sub-kegiatan pattern (e.g., 5.02.01.2.01.0001 or has 4-digit suffix)
    parts = kode.rstrip('.').split('.')
    if len(parts) >= 6 or (pj_raw and len(parts) >= 5):
        pj = fix_pj(pj_raw, uraian)

        # Calculate monthly cumulative realization
        running_realisasi = 0.0
        for m_idx, m_name in enumerate(months, 1):
            val_month = float(row.get(m_name, 0.0))
            running_realisasi += val_month

            rows_list.append({
                "tahun": 2025,
                "nama_opd": "Badan Keuangan dan Aset Daerah (BKAD)",
                "penanggungjawab": pj,
                "kode_rekening": kode,
                "jenis_belanja": uraian,
                "bulan": m_idx,
                "pagu_anggaran": pagu,
                "realisasi": running_realisasi,
            })

df_clean = pd.DataFrame(rows_list)

print(f"Generated {len(df_clean)} rows of data for BKAD.")
print("Penanggungjawab categories:", df_clean["penanggungjawab"].unique())
print("Total Sub-kegiatan:", df_clean["jenis_belanja"].nunique())

os.makedirs("data", exist_ok=True)
out_file = "data/dummy_data.xlsx"
df_clean.to_excel(out_file, index=False, sheet_name="Realisasi Anggaran")
print(f"Saved real data to {out_file}")
