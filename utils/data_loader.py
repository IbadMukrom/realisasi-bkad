"""
Modul untuk memuat dan memproses data realisasi anggaran BKAD dari file Excel.
"""
import pandas as pd
import streamlit as st


from typing import Optional, List

REQUIRED_COLUMNS = [
    "tahun", "nama_opd", "jenis_belanja", "bulan",
    "pagu_anggaran", "realisasi"
]


NAMA_BULAN = {
    1: "Januari", 2: "Februari", 3: "Maret",
    4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September",
    10: "Oktober", 11: "November", 12: "Desember",
}

NAMA_TRIWULAN = {
    1: "Triwulan I (Jan-Mar)",
    2: "Triwulan II (Apr-Jun)",
    3: "Triwulan III (Jul-Sep)",
    4: "Triwulan IV (Okt-Des)",
}


def _process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalisasi kolom, validasi, dan tambah kolom turunan.
    """
    # Normalisasi nama kolom: lowercase, strip spasi
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Validasi kolom
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Kolom berikut tidak ditemukan dalam file: {', '.join(missing)}. "
            f"Kolom yang tersedia: {', '.join(df.columns)}"
        )

    # Pastikan tipe data numerik
    df["pagu_anggaran"] = pd.to_numeric(df["pagu_anggaran"], errors="coerce").fillna(0)
    df["realisasi"] = pd.to_numeric(df["realisasi"], errors="coerce").fillna(0)
    df["bulan"] = pd.to_numeric(df["bulan"], errors="coerce").fillna(1).astype(int)
    df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce").fillna(2024).astype(int)

    # Tambah kolom turunan
    df["nama_bulan"] = df["bulan"].map(NAMA_BULAN)
    df["triwulan"] = ((df["bulan"] - 1) // 3 + 1)
    df["nama_triwulan"] = df["triwulan"].map(NAMA_TRIWULAN)
    df["sisa_anggaran"] = df["pagu_anggaran"] - df["realisasi"]
    df["persentase_realisasi"] = (
        (df["realisasi"] / df["pagu_anggaran"] * 100)
        .round(2)
        .fillna(0)
    )

    return df


def read_smart_excel(source) -> pd.DataFrame:
    """
    Membaca file Excel dengan cerdas: mengutamakan sheet 'Data Realisasi'
    atau 'Realisasi Anggaran' yang memiliki kolom wajib realisasi.
    """
    try:
        excel_file = pd.ExcelFile(source)
        sheet_names = excel_file.sheet_names

        # 1. Utamakan sheet "Data Realisasi" atau "Realisasi Anggaran" jika valid
        for preferred in ["Data Realisasi", "Realisasi Anggaran"]:
            if preferred in sheet_names:
                try:
                    df_temp = pd.read_excel(source, sheet_name=preferred)
                    norm_cols = df_temp.columns.str.strip().str.lower().str.replace(" ", "_")
                    if all(col in norm_cols for col in REQUIRED_COLUMNS):
                        return df_temp
                except Exception:
                    pass

        # 2. Periksa sheet lain yang memiliki kolom REQUIRED_COLUMNS
        for sheet in sheet_names:
            try:
                df_temp = pd.read_excel(source, sheet_name=sheet)
                norm_cols = df_temp.columns.str.strip().str.lower().str.replace(" ", "_")
                if all(col in norm_cols for col in REQUIRED_COLUMNS):
                    return df_temp
            except Exception:
                continue

        # 3. Fallback: baca sheet index 0
        return pd.read_excel(source, sheet_name=0)
    except Exception:
        return pd.read_excel(source)


@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    """
    Membaca file Excel dan memvalidasi kolom yang diperlukan.
    """
    df = read_smart_excel(filepath)
    return _process_dataframe(df)


def load_uploaded_data(uploaded_file) -> pd.DataFrame:
    """
    Membaca file Excel yang di-upload user melalui Streamlit file_uploader.
    """
    df = read_smart_excel(uploaded_file)
    return _process_dataframe(df)


def filter_data(
    df: pd.DataFrame,
    tahun: Optional[int] = None,
    penanggungjawab_list: Optional[List[str]] = None,
    jenis_belanja_list: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Filter DataFrame berdasarkan pilihan user.
    """
    filtered = df.copy()

    if tahun is not None:
        filtered = filtered[filtered["tahun"] == tahun]

    if penanggungjawab_list and len(penanggungjawab_list) > 0 and "penanggungjawab" in filtered.columns:
        filtered = filtered[filtered["penanggungjawab"].isin(penanggungjawab_list)]

    if jenis_belanja_list and len(jenis_belanja_list) > 0:
        filtered = filtered[filtered["jenis_belanja"].isin(jenis_belanja_list)]

    return filtered


def get_summary(df: pd.DataFrame) -> dict:
    """
    Menghitung ringkasan data: total pagu, realisasi, sisa, persentase.
    Mengambil data bulan terakhir per item kegiatan/jenis belanja.
    """
    group_cols = ["jenis_belanja"]
    if "penanggungjawab" in df.columns:
        group_cols.insert(0, "penanggungjawab")
    if "kode_rekening" in df.columns:
        group_cols.insert(0, "kode_rekening")

    idx = df.groupby(group_cols)["bulan"].idxmax()
    latest = df.loc[idx]

    total_pagu = latest["pagu_anggaran"].sum()
    total_realisasi = latest["realisasi"].sum()
    total_sisa = total_pagu - total_realisasi
    persentase = (total_realisasi / total_pagu * 100) if total_pagu > 0 else 0

    return {
        "total_pagu": total_pagu,
        "total_realisasi": total_realisasi,
        "total_sisa": total_sisa,
        "persentase": round(persentase, 2),
    }


def get_pj_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perbandingan pagu vs realisasi per Bidang Penanggung Jawab.
    """
    if "penanggungjawab" not in df.columns:
        return pd.DataFrame()

    group_cols = ["penanggungjawab", "jenis_belanja"]
    if "kode_rekening" in df.columns:
        group_cols.insert(0, "kode_rekening")

    idx = df.groupby(group_cols)["bulan"].idxmax()
    latest = df.loc[idx]

    pj_df = (
        latest
        .groupby("penanggungjawab")
        .agg(
            pagu_anggaran=("pagu_anggaran", "sum"),
            realisasi=("realisasi", "sum"),
        )
        .reset_index()
    )
    pj_df["sisa"] = pj_df["pagu_anggaran"] - pj_df["realisasi"]
    pj_df["persentase"] = (
        (pj_df["realisasi"] / pj_df["pagu_anggaran"] * 100)
        .round(2)
        .fillna(0)
    )
    pj_df = pj_df.sort_values("persentase", ascending=False)
    return pj_df


def get_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregasi realisasi kumulatif per bulan.
    """
    monthly = (
        df
        .groupby("bulan")
        .agg(
            realisasi_kumulatif=("realisasi", "sum"),
            pagu_anggaran=("pagu_anggaran", "sum"),
        )
        .reset_index()
    )
    monthly["nama_bulan"] = monthly["bulan"].map(NAMA_BULAN)

    return monthly


def get_quarterly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregasi realisasi per triwulan.
    """
    df_copy = df.copy()
    df_copy["triwulan"] = ((df_copy["bulan"] - 1) // 3 + 1)

    idx = df_copy.groupby(["jenis_belanja", "triwulan"])["bulan"].idxmax()
    latest_per_q = df_copy.loc[idx]

    quarterly = (
        latest_per_q
        .groupby("triwulan")
        .agg(
            realisasi_kumulatif=("realisasi", "sum"),
            pagu_anggaran=("pagu_anggaran", "sum"),
        )
        .reset_index()
    )
    quarterly["nama_triwulan"] = quarterly["triwulan"].map(NAMA_TRIWULAN)
    quarterly["persentase"] = (
        quarterly["realisasi_kumulatif"] / quarterly["pagu_anggaran"] * 100
    ).round(2)

    return quarterly


def get_belanja_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perbandingan pagu vs realisasi per jenis belanja / sub-kegiatan.
    """
    group_cols = ["jenis_belanja"]
    if "penanggungjawab" in df.columns:
        group_cols.insert(0, "penanggungjawab")
    if "kode_rekening" in df.columns:
        group_cols.insert(0, "kode_rekening")

    idx = df.groupby(group_cols)["bulan"].idxmax()
    latest = df.loc[idx]

    comparison = (
        latest
        .groupby("jenis_belanja")
        .agg(
            pagu_anggaran=("pagu_anggaran", "sum"),
            realisasi=("realisasi", "sum"),
        )
        .reset_index()
    )
    comparison["sisa"] = comparison["pagu_anggaran"] - comparison["realisasi"]
    comparison["persentase"] = (
        (comparison["realisasi"] / comparison["pagu_anggaran"] * 100)
        .round(2)
        .fillna(0)
    )
    comparison = comparison.sort_values("persentase", ascending=False)

    return comparison


def get_belanja_composition(df: pd.DataFrame) -> pd.DataFrame:
    """
    Komposisi realisasi per jenis belanja / sub-kegiatan.
    """
    group_cols = ["jenis_belanja"]
    if "penanggungjawab" in df.columns:
        group_cols.insert(0, "penanggungjawab")
    if "kode_rekening" in df.columns:
        group_cols.insert(0, "kode_rekening")

    idx = df.groupby(group_cols)["bulan"].idxmax()
    latest = df.loc[idx]

    composition = (
        latest
        .groupby("jenis_belanja")
        .agg(
            pagu_anggaran=("pagu_anggaran", "sum"),
            realisasi=("realisasi", "sum"),
        )
        .reset_index()
    )
    total = composition["realisasi"].sum()
    composition["persentase_komposisi"] = (
        (composition["realisasi"] / total * 100)
        .round(2)
        .fillna(0)
    ) if total > 0 else 0

    return composition
