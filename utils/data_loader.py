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
    if df.empty:
        return df.copy()

    df = df.copy()
    # Normalisasi nama kolom: lowercase, strip spasi
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Validasi kolom
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            f"Kolom berikut tidak ditemukan dalam file: {', '.join(missing)}. "
            f"Kolom yang tersedia: {', '.join(df.columns)}"
        )

    # Pastikan tipe data numerik dan bersihkan string
    df["pagu_anggaran"] = pd.to_numeric(df["pagu_anggaran"], errors="coerce").fillna(0)
    df["realisasi"] = pd.to_numeric(df["realisasi"], errors="coerce").fillna(0)
    df["bulan"] = pd.to_numeric(df["bulan"], errors="coerce").fillna(1).astype(int)
    df["tahun"] = pd.to_numeric(df["tahun"], errors="coerce").fillna(2025).astype(int)

    if "penanggungjawab" in df.columns:
        df["penanggungjawab"] = df["penanggungjawab"].fillna("Sekretariat").astype(str).str.strip()
    else:
        df["penanggungjawab"] = "Sekretariat"

    if "kode_rekening" in df.columns:
        df["kode_rekening"] = df["kode_rekening"].fillna("").astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    else:
        df["kode_rekening"] = ""

    if "jenis_belanja" in df.columns:
        df["jenis_belanja"] = df["jenis_belanja"].fillna("").astype(str).str.strip()
    else:
        df["jenis_belanja"] = ""

    # Tambah kolom turunan
    df["nama_bulan"] = df["bulan"].map(NAMA_BULAN)
    df["triwulan"] = ((df["bulan"] - 1) // 3 + 1)
    df["nama_triwulan"] = df["triwulan"].map(NAMA_TRIWULAN)

    group_cols = [c for c in ["tahun", "penanggungjawab", "kode_rekening", "jenis_belanja"] if c in df.columns]
    if not group_cols:
        group_cols = ["tahun", "jenis_belanja"]

    # Urutkan berdasarkan urutan bulan untuk akumulasi
    df = df.sort_values(group_cols + ["bulan"])

    # Hitung Realisasi Kumulatif (terakumulasi dari bulan ke bulan per item)
    df["realisasi_kumulatif"] = df.groupby(group_cols, dropna=False)["realisasi"].cumsum()
    df["sisa_anggaran"] = df["pagu_anggaran"] - df["realisasi_kumulatif"]
    df["persentase_realisasi"] = (
        (df["realisasi_kumulatif"] / df["pagu_anggaran"].replace(0, 1) * 100)
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


@st.cache_data(ttl="5s", show_spinner=False)
def load_data(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Membaca data mentah (Google Sheets/Excel) dan memproses kolom turunan & akumulasi.
    """
    from utils.data_manager import load_raw_data
    df = load_raw_data(filepath)
    if df.empty:
        return df
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


TARGET_TRIWULAN = {
    1: 15.0,  # TW I (Jan-Mar)
    2: 40.0,  # TW II (Apr-Jun)
    3: 75.0,  # TW III (Jul-Sep)
    4: 100.0, # TW IV (Okt-Des)
}

TARGET_BULANAN = {
    1: 5.0,
    2: 10.0,
    3: 15.0,
    4: 23.0,
    5: 31.0,
    6: 40.0,
    7: 51.0,
    8: 63.0,
    9: 75.0,
    10: 83.0,
    11: 91.0,
    12: 100.0,
}


def get_summary(df: pd.DataFrame) -> dict:
    """
    Menghitung ringkasan data:
    - Total Pagu Tahunan: Pagu tetap (diambil 1x per item unik per tahun, tidak terakumulasi antar bulan).
    - Total Realisasi: Realisasi kumulatif terakumulasi s.d. bulan terakhir.
    """
    if df.empty:
        return {
            "total_pagu": 0.0,
            "total_realisasi": 0.0,
            "total_sisa": 0.0,
            "persentase": 0.0,
            "latest_bulan": 1,
        }

    item_cols = [c for c in ["tahun", "penanggungjawab", "kode_rekening", "jenis_belanja"] if c in df.columns]
    if not item_cols:
        item_cols = ["jenis_belanja"]

    # Total Pagu Tahunan (TETAP: 1x per item unik)
    total_pagu = df.groupby(item_cols, dropna=False)["pagu_anggaran"].first().sum()

    # Total Realisasi (Terakumulasi s.d. bulan terakhir per item)
    idx = df.groupby(item_cols, dropna=False)["bulan"].idxmax()
    latest = df.loc[idx].copy()
    real_col = "realisasi_kumulatif" if "realisasi_kumulatif" in latest.columns else "realisasi"
    total_realisasi = latest[real_col].sum()

    latest_bulan = int(latest["bulan"].max()) if not latest.empty and "bulan" in latest.columns else 1

    total_sisa = max(0.0, total_pagu - total_realisasi)
    persentase = (total_realisasi / total_pagu * 100) if total_pagu > 0 else 0.0

    return {
        "total_pagu": total_pagu,
        "total_realisasi": total_realisasi,
        "total_sisa": total_sisa,
        "persentase": round(persentase, 2),
        "latest_bulan": latest_bulan,
    }


def get_pj_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perbandingan pagu vs realisasi kumulatif per Bidang Penanggung Jawab.
    """
    if "penanggungjawab" not in df.columns or df.empty:
        return pd.DataFrame()

    group_cols = ["penanggungjawab", "jenis_belanja"]
    if "kode_rekening" in df.columns:
        group_cols.insert(0, "kode_rekening")

    idx = df.groupby(group_cols)["bulan"].idxmax()
    latest = df.loc[idx]

    real_col = "realisasi_kumulatif" if "realisasi_kumulatif" in latest.columns else "realisasi"

    pj_df = (
        latest
        .groupby("penanggungjawab")
        .agg(
            pagu_anggaran=("pagu_anggaran", "sum"),
            realisasi=(real_col, "sum"),
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
    Agregasi realisasi kumulatif terakumulasi per bulan.
    Pagu Anggaran Tahunan nilainya TETAP (tidak dijumlahkan per bulan).
    """
    if df.empty:
        return pd.DataFrame()

    group_cols = [c for c in ["tahun", "penanggungjawab", "kode_rekening", "jenis_belanja"] if c in df.columns]
    if not group_cols:
        group_cols = ["jenis_belanja"]

    real_col = "realisasi_kumulatif" if "realisasi_kumulatif" in df.columns else "realisasi"

    monthly = (
        df
        .groupby("bulan")
        .agg(
            realisasi_kumulatif=(real_col, "sum"),
        )
        .reset_index()
    )
    monthly["nama_bulan"] = monthly["bulan"].map(NAMA_BULAN)

    idx = df.groupby(group_cols)["bulan"].idxmax()
    latest = df.loc[idx]
    monthly["pagu_anggaran"] = latest["pagu_anggaran"].sum()

    return monthly


def get_quarterly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agregasi realisasi per triwulan dengan Pagu Anggaran Tahunan yang TETAP.
    """
    if df.empty:
        return pd.DataFrame()

    df_copy = df.copy()
    df_copy["triwulan"] = ((df_copy["bulan"] - 1) // 3 + 1)

    group_cols = [c for c in ["tahun", "penanggungjawab", "kode_rekening", "jenis_belanja"] if c in df.columns]
    if not group_cols:
        group_cols = ["jenis_belanja"]

    real_col = "realisasi_kumulatif" if "realisasi_kumulatif" in df_copy.columns else "realisasi"

    idx = df_copy.groupby(group_cols + ["triwulan"])["bulan"].idxmax()
    latest_per_q = df_copy.loc[idx]

    quarterly = (
        latest_per_q
        .groupby("triwulan")
        .agg(
            realisasi_kumulatif=(real_col, "sum"),
        )
        .reset_index()
    )

    idx_annual = df.groupby(group_cols)["bulan"].idxmax()
    total_pagu = df.loc[idx_annual]["pagu_anggaran"].sum()

    quarterly["pagu_anggaran"] = total_pagu
    quarterly["nama_triwulan"] = quarterly["triwulan"].map(NAMA_TRIWULAN)
    quarterly["persentase"] = (
        (quarterly["realisasi_kumulatif"] / total_pagu * 100).round(2) if total_pagu > 0 else 0
    )

    return quarterly


def get_belanja_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perbandingan pagu vs realisasi per jenis belanja / sub-kegiatan.
    Pagu Anggaran dengan nama jenis belanja yang sama nilainya TETAP (tidak terakumulasi per bulan).
    """
    if df.empty:
        return pd.DataFrame()

    group_cols = [c for c in ["tahun", "penanggungjawab", "kode_rekening", "jenis_belanja"] if c in df.columns]
    if not group_cols:
        group_cols = ["jenis_belanja"]

    idx = df.groupby(group_cols)["bulan"].idxmax()
    latest = df.loc[idx]

    real_col = "realisasi_kumulatif" if "realisasi_kumulatif" in latest.columns else "realisasi"

    comparison = (
        latest
        .groupby("jenis_belanja")
        .agg(
            pagu_anggaran=("pagu_anggaran", "first"),  # Pagu tetap per jenis belanja
            realisasi=(real_col, "sum"),
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
    if df.empty:
        return pd.DataFrame()

    group_cols = [c for c in ["tahun", "penanggungjawab", "kode_rekening", "jenis_belanja"] if c in df.columns]
    if not group_cols:
        group_cols = ["jenis_belanja"]

    idx = df.groupby(group_cols)["bulan"].idxmax()
    latest = df.loc[idx]

    real_col = "realisasi_kumulatif" if "realisasi_kumulatif" in latest.columns else "realisasi"

    composition = (
        latest
        .groupby("jenis_belanja")
        .agg(
            pagu_anggaran=("pagu_anggaran", "first"),  # Pagu tetap per jenis belanja
            realisasi=(real_col, "sum"),
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


def get_executive_insights(df: pd.DataFrame, summary: dict) -> dict:
    """
    Menghasilkan narasi dan insight eksekutif otomatis dari data realisasi.
    """
    if df.empty:
        return {
            "top_sub": None,
            "lowest_sub": None,
            "top_pj": None,
            "bullets": ["Belum ada data anggaran yang tersedia."],
        }

    group_cols = [c for c in ["tahun", "penanggungjawab", "kode_rekening", "jenis_belanja"] if c in df.columns]
    if not group_cols:
        group_cols = ["jenis_belanja"]

    idx = df.groupby(group_cols, dropna=False)["bulan"].idxmax()
    latest = df.loc[idx].copy()
    real_col = "realisasi_kumulatif" if "realisasi_kumulatif" in latest.columns else "realisasi"
    latest["persentase"] = (latest[real_col] / latest["pagu_anggaran"].replace(0, 1) * 100).round(2)

    # Sub-kegiatan tertinggi & terendah
    sorted_sub = latest.sort_values("persentase", ascending=False)
    top_sub_row = sorted_sub.iloc[0] if not sorted_sub.empty else None
    lowest_sub_row = sorted_sub.iloc[-1] if not sorted_sub.empty else None

    # Bidang penanggung jawab paling produktif
    top_pj_row = None
    if "penanggungjawab" in latest.columns:
        pj_agg = latest.groupby("penanggungjawab").agg(
            pagu=("pagu_anggaran", "sum"),
            real=(real_col, "sum"),
        ).reset_index()
        pj_agg["pct"] = (pj_agg["real"] / pj_agg["pagu"].replace(0, 1) * 100).round(2)
        pj_agg = pj_agg.sort_values("pct", ascending=False)
        if not pj_agg.empty:
            top_pj_row = pj_agg.iloc[0]

    latest_bln_name = NAMA_BULAN.get(summary.get("latest_bulan", 1), "berjalan")
    total_pct = summary.get("persentase", 0.0)

    bullets = []

    # Bullet 1: Ringkasan Capaian Overall
    bullets.append(f"Capaian realisasi keseluruhan s.d. bulan **{latest_bln_name}** mencapai **{total_pct:.2f}%** dari total pagu anggaran.")

    # Bullet 2: Sub-kegiatan tertinggi
    if top_sub_row is not None:
        sub_name = top_sub_row["jenis_belanja"]
        sub_pct = top_sub_row["persentase"]
        bullets.append(f"Sub-kegiatan dengan capaian tertinggi saat ini adalah **{sub_name}** (**{sub_pct:.2f}%**).")

    # Bullet 3: Sub-kegiatan terendah
    if lowest_sub_row is not None and len(sorted_sub) > 1:
        low_name = lowest_sub_row["jenis_belanja"]
        low_pct = lowest_sub_row["persentase"]
        bullets.append(f"Sub-kegiatan dengan capaian terendah saat ini adalah **{low_name}** (**{low_pct:.2f}%**).")

    # Bullet 4: Bidang terbaik
    if top_pj_row is not None:
        bullets.append(f"Bidang Penanggung Jawab dengan capaian tertinggi adalah **{top_pj_row['penanggungjawab']}** (**{top_pj_row['pct']:.2f}%**).")

    return {
        "top_sub": top_sub_row.to_dict() if top_sub_row is not None else None,
        "lowest_sub": lowest_sub_row.to_dict() if lowest_sub_row is not None else None,
        "top_pj": top_pj_row.to_dict() if top_pj_row is not None else None,
        "bullets": bullets,
    }
