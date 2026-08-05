"""
Modul untuk mengelola data anggaran — simpan, update, hapus ke file Excel.
"""
import pandas as pd
import os

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


def get_all_jenis_belanja(filepath: Optional[str] = None) -> List[str]:
    """
    Mendapatkan daftar seluruh jenis belanja dari file Excel + default options.
    """
    df = load_raw_data(filepath)
    existing = []
    if not df.empty and "jenis_belanja" in df.columns:
        existing = [str(x).strip() for x in df["jenis_belanja"].dropna().unique() if str(x).strip()]
    
    combined = list(dict.fromkeys(JENIS_BELANJA_OPTIONS + existing))
    return sorted(combined)


def get_all_penanggungjawab(filepath: Optional[str] = None) -> List[str]:
    """
    Mendapatkan daftar Bidang Penanggung Jawab dari file Excel.
    """
    df = load_raw_data(filepath)
    if not df.empty and "penanggungjawab" in df.columns:
        return sorted([str(x).strip() for x in df["penanggungjawab"].dropna().unique() if str(x).strip()])
    return [
        "Sekretariat",
        "Bidang Anggaran",
        "Bidang Perbendaharaan",
        "Bidang Akuntansi & Pelaporan",
        "Bidang Pengelolaan BMD",
    ]


def get_data_path() -> str:
    """Mendapatkan path file data Excel."""
    return DEFAULT_FILE


from utils.data_loader import read_smart_excel


def load_raw_data(filepath: Optional[str] = None) -> pd.DataFrame:
    """
    Membaca data mentah dari file Excel tanpa caching menggunakan smart Excel reader.
    """
    path = filepath or DEFAULT_FILE
    if not os.path.exists(path):
        # Buat file kosong jika belum ada
        df = pd.DataFrame(columns=[
            "tahun", "nama_opd", "penanggungjawab", "kode_rekening",
            "jenis_belanja", "bulan", "pagu_anggaran", "realisasi"
        ])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_excel(path, index=False, sheet_name="Realisasi Anggaran")
        return df

    try:
        df = read_smart_excel(path)
    except Exception:
        df = pd.read_excel(path)

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def save_data(df: pd.DataFrame, filepath: Optional[str] = None) -> None:
    """
    Menyimpan DataFrame ke file Excel.
    """
    path = filepath or DEFAULT_FILE
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Pastikan kolom yang disimpan benar
    save_cols = ["tahun", "nama_opd", "penanggungjawab", "kode_rekening", "jenis_belanja", "bulan", "pagu_anggaran", "realisasi"]
    existing_cols = [c for c in save_cols if c in df.columns]
    df[existing_cols].to_excel(path, index=False, sheet_name="Realisasi Anggaran")


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
