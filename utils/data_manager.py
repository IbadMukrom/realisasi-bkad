"""
Modul untuk mengelola data anggaran — simpan, update, hapus ke file Excel atau Google Sheets.
"""
import pandas as pd
import os
import streamlit as st

from typing import Optional, List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DEFAULT_FILE = os.path.join(DATA_DIR, "dummy_data.xlsx")

NAMA_OPD = "Badan Keuangan dan Aset Daerah (BKAD)"

JENIS_BELANJA_OPTIONS = [
    "Belanja Pegawai",
    "Belanja Barang dan Jasa",
    "Belanja Modal",
    "Belanja Hibah",
    "Belanja Bantuan Sosial",
    "Belanja Tidak Terduga",
    "Belanja Transfer",
]

NAMA_BULAN = {
    1: "Januari", 2: "Februari", 3: "Maret",
    4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September",
    10: "Oktober", 11: "November", 12: "Desember",
}


def is_gsheets_configured() -> bool:
    """Memeriksa apakah koneksi Google Sheets sudah dikonfigurasi di secrets."""
    try:
        return "connections" in st.secrets and "gsheets" in st.secrets["connections"]
    except Exception:
        return False


def get_gsheets_connection():
    """Mendapatkan objek koneksi Google Sheets."""
    from streamlit_gsheets import GSheetsConnection
    return st.connection("gsheets", type=GSheetsConnection)


def get_all_jenis_belanja(filepath: Optional[str] = None) -> List[str]:
    """
    Mendapatkan daftar seluruh jenis belanja dari Excel/Google Sheets + default options.
    """
    df = load_raw_data(filepath)
    existing = []
    if not df.empty and "jenis_belanja" in df.columns:
        existing = [str(x).strip() for x in df["jenis_belanja"].dropna().unique() if str(x).strip()]
    
    combined = list(dict.fromkeys(JENIS_BELANJA_OPTIONS + existing))
    return sorted(combined)


def get_all_penanggungjawab(filepath: Optional[str] = None) -> List[str]:
    """
    Mendapatkan daftar Bidang Penanggung Jawab dari Excel/Google Sheets.
    """
    defaults = [
        "Sekretariat",
        "Bidang Anggaran",
        "Bidang Perbendaharaan",
        "Bidang Akuntansi & Pelaporan",
        "Bidang Pengelolaan BMD",
    ]
    df = load_raw_data(filepath)
    if not df.empty and "penanggungjawab" in df.columns:
        existing = [str(x).strip() for x in df["penanggungjawab"].dropna().unique() if str(x).strip()]
        combined = list(dict.fromkeys(defaults + existing))
        return sorted(combined)
    return defaults


def get_data_path() -> str:
    """Mendapatkan path file data Excel."""
    return DEFAULT_FILE


def load_raw_data(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Membaca data mentah dari Google Sheets (jika dikonfigurasi) atau dari file Excel.
    """
    if is_gsheets_configured():
        try:
            conn = get_gsheets_connection()
            df = conn.read(worksheet="Realisasi Anggaran", ttl="0s")
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
            if not df.empty:
                return df
        except Exception as e:
            st.warning(f"⚠️ Gagal membaca Google Sheets, beralih ke data lokal: {e}")

    path = filepath or DEFAULT_FILE
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            import generate_dummy
        except Exception:
            pass

    try:
        from utils.data_loader import read_smart_excel
        df = read_smart_excel(path)
    except Exception:
        df = pd.read_excel(path)

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    if df.empty:
        try:
            import generate_dummy
            from utils.data_loader import read_smart_excel
            df = read_smart_excel(path)
            df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        except Exception:
            pass

    return df


def save_data(df: pd.DataFrame, filepath: Optional[str] = None) -> None:
    """
    Menyimpan DataFrame ke Google Sheets (jika dikonfigurasi) dan/atau file Excel lokal.
    """
    save_cols = ["tahun", "nama_opd", "penanggungjawab", "kode_rekening", "jenis_belanja", "bulan", "pagu_anggaran", "realisasi"]
    existing_cols = [c for c in save_cols if c in df.columns]
    clean_df = df[existing_cols]

    if is_gsheets_configured():
        try:
            conn = get_gsheets_connection()
            conn.update(worksheet="Realisasi Anggaran", data=clean_df)
            st.cache_data.clear()
        except Exception as e:
            st.error(f"❌ Gagal menyimpan ke Google Sheets: {e}")

    # Simpan juga ke file Excel lokal sebagai cadangan
    path = filepath or DEFAULT_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)
    clean_df.to_excel(path, index=False, sheet_name="Realisasi Anggaran")


def add_record(
    tahun: int,
    jenis_belanja: str,
    bulan: int,
    pagu_anggaran: float,
    realisasi: float,
    penanggungjawab: str = "Sekretariat",
    kode_rekening: str = "",
    filepath: Optional[str] = None,
) -> pd.DataFrame:
    """
    Menambah satu baris data baru.
    """
    df = load_raw_data(filepath)

    new_row = pd.DataFrame([{
        "tahun": tahun,
        "nama_opd": NAMA_OPD,
        "penanggungjawab": penanggungjawab,
        "kode_rekening": kode_rekening,
        "jenis_belanja": jenis_belanja,
        "bulan": bulan,
        "pagu_anggaran": pagu_anggaran,
        "realisasi": realisasi,
    }])

    df = pd.concat([df, new_row], ignore_index=True)
    df = df.sort_values(["tahun", "jenis_belanja", "bulan"]).reset_index(drop=True)
    save_data(df, filepath)
    return df


def update_record(
    idx: int,
    data: Dict[str, Any],
    filepath: Optional[str] = None,
) -> pd.DataFrame:
    """
    Mengupdate satu baris data berdasarkan index.
    """
    df = load_raw_data(filepath)

    if idx < 0 or idx >= len(df):
        raise ValueError(f"Index {idx} tidak valid.")

    for key, value in data.items():
        if key in df.columns:
            df.at[idx, key] = value

    save_data(df, filepath)
    return df


def delete_records(
    indices: List[int],
    filepath: Optional[str] = None,
) -> pd.DataFrame:
    """
    Menghapus baris data berdasarkan list index.
    """
    df = load_raw_data(filepath)
    df = df.drop(index=indices).reset_index(drop=True)
    save_data(df, filepath)
    return df


def bulk_save(df: pd.DataFrame, filepath: Optional[str] = None) -> None:
    """
    Menyimpan seluruh DataFrame yang sudah diedit (dari st.data_editor).
    """
    path = filepath or DEFAULT_FILE

    # Pastikan kolom nama_opd terisi
    if "nama_opd" not in df.columns:
        df["nama_opd"] = NAMA_OPD
    else:
        df["nama_opd"] = df["nama_opd"].fillna(NAMA_OPD)

    save_data(df, path)
