"""
Dashboard Visualisasi Realisasi Anggaran BKAD
==============================================
Aplikasi Streamlit untuk memvisualisasikan dan mengelola data realisasi anggaran
Badan Keuangan dan Aset Daerah (BKAD).
"""
import streamlit as st
import pandas as pd
import os

from utils.data_loader import (
    load_data,
    load_uploaded_data,
    read_smart_excel,
    filter_data,
    get_summary,
    get_executive_insights,
    get_pj_comparison,
    get_monthly_trend,
    get_quarterly_trend,
    get_belanja_comparison,
    get_belanja_composition,
    NAMA_BULAN,
)
from utils.charts import (
    create_gauge_chart,
    create_trend_chart,
    create_belanja_comparison,
    create_pj_comparison,
    create_donut_chart,
    create_heatmap_belanja_monthly,
    format_rupiah,
    format_rupiah_titik,
    parse_rupiah_input,
)
from utils.data_manager import (
    load_raw_data,
    add_record,
    delete_records,
    bulk_save,
    merge_save_records,
    validate_and_sanitize_excel,
    get_data_path,
    get_all_jenis_belanja,
    get_all_penanggungjawab,
    is_gsheets_configured,
    generate_formatted_excel_report,
    generate_formatted_pdf_report,
    JENIS_BELANJA_OPTIONS,
)
from utils.auth import (
    is_authenticated,
    render_login_box,
    logout,
)


# ─── Helper Functions ─────────────────────────────────────────────────────────

def safe_sorted_options(series) -> list:
    """Mengembalikan list string unik yang terurut secara aman dari Series (bebas dari error NaN/None/mixed types)."""
    if series is None or len(series) == 0:
        return []
    cleaned = [str(x).strip() for x in pd.Series(series).dropna().unique() if pd.notna(x) and str(x).strip() != "" and str(x).lower() != "nan"]
    return sorted(list(set(cleaned)))


def safe_sorted_years(series) -> list:
    """Mengembalikan list integer tahun yang terurut secara aman dari Series."""
    if series is None or len(series) == 0:
        return [2025]
    years = []
    for x in pd.Series(series).dropna().unique():
        if pd.notna(x):
            try:
                val = int(float(x))
                years.append(val)
            except (ValueError, TypeError):
                pass
    return sorted(list(set(years))) if years else [2025]


# ─── Page Config ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Dashboard Realisasi Anggaran BKAD",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── Custom CSS ──────────────────────────────────────────────────────────────

# ─── Custom CSS ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 98% !important;
    }

    /* Header Banner Premium */
    .main-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 40%, #064E3B 100%);
        padding: 2.2rem 2.8rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 230, 118, 0.25);
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4), inset 0 1px 1px rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0,230,118,0.06) 0%, transparent 60%);
        pointer-events: none;
    }
    .main-header h1 {
        color: #F8FAFC;
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.03em;
        text-shadow: 0 2px 8px rgba(0,0,0,0.5);
    }
    .main-header p {
        color: #94A3B8;
        font-size: 1rem;
        margin: 0.6rem 0 0 0;
        font-weight: 400;
    }
    .main-header .opd-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 230, 118, 0.12);
        color: #00E676;
        padding: 0.4rem 1rem;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-top: 1rem;
        border: 1px solid rgba(0, 230, 118, 0.35);
        box-shadow: 0 0 12px rgba(0, 230, 118, 0.15);
    }

    /* Glassmorphism Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        backdrop-filter: blur(16px);
        padding: 1.5rem 1.6rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(0, 230, 118, 0.4);
        box-shadow: 0 14px 36px rgba(0, 0, 0, 0.45), 0 0 20px rgba(0, 230, 118, 0.1);
    }
    .metric-label {
        color: #94A3B8;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.6rem;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.65rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.25;
        letter-spacing: -0.02em;
    }
    .metric-value.green { color: #00E676; text-shadow: 0 0 12px rgba(0, 230, 118, 0.25); }
    .metric-value.blue { color: #29B6F6; text-shadow: 0 0 12px rgba(41, 182, 246, 0.25); }
    .metric-value.red { color: #FF5252; text-shadow: 0 0 12px rgba(255, 82, 82, 0.25); }
    .metric-value.orange { color: #FFCA28; text-shadow: 0 0 12px rgba(255, 202, 40, 0.25); }

    /* Section Headers */
    .section-header {
        color: #F8FAFC;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 2.2rem 0 1.2rem 0;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid transparent;
        border-image: linear-gradient(to right, #00E676 0%, #29B6F6 40%, transparent 100%) 1;
        letter-spacing: -0.01em;
    }

    /* Sidebar Custom Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B0F19 0%, #151D2A 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #00E676;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: -0.01em;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0, 230, 118, 0.35), transparent);
        margin: 1.8rem 0;
    }

    /* Badges */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.85rem;
        border-radius: 25px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-top: 0.6rem;
    }
    .status-good { background: rgba(0, 230, 118, 0.15); color: #00E676; border: 1px solid rgba(0, 230, 118, 0.3); }
    .status-warning { background: rgba(255, 202, 40, 0.15); color: #FFCA28; border: 1px solid rgba(255, 202, 40, 0.3); }
    .status-danger { background: rgba(255, 82, 82, 0.15); color: #FF5252; border: 1px solid rgba(255, 82, 82, 0.3); }

    /* Form and Section Box */
    .form-section {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        backdrop-filter: blur(12px);
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        font-weight: 700 !important;
        font-size: 1rem !important;
        color: #F8FAFC !important;
        background: rgba(30, 41, 59, 0.6) !important;
        border-radius: 12px !important;
    }

    /* Primary Button Polish */
    div.stButton > button[kind="primary"], div.stDownloadButton > button[kind="primary"] {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.65rem 1.4rem !important;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.25s ease !important;
    }
    div.stButton > button[kind="primary"]:hover, div.stDownloadButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.45) !important;
    }
</style>
""", unsafe_allow_html=True)


# ─── Sidebar Navigation ─────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🧭 Navigasi")
    page = st.radio(
        "Pilih Halaman",
        options=["📊 Dashboard", "📝 Kelola Data", "📖 Panduan"],
        label_visibility="collapsed",
    )

    if is_authenticated():
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown("🔒 **Status Sesi:**")
        st.caption(f"Login sebagai: **{st.session_state.get('username', 'Admin')}**")
        if st.button("🚪 Keluar (Logout)", use_container_width=True):
            logout()
            st.success("✅ Berhasil logout.")
            st.rerun()

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: KELOLA DATA
# ═══════════════════════════════════════════════════════════════════════════════

if page == "📝 Kelola Data":

    if not is_authenticated():
        render_login_box()
        st.stop()

    st.markdown("""
    <div class="main-header">
        <h1>📝 Kelola Data Anggaran</h1>
        <p>Tambah, edit, dan hapus data realisasi anggaran BKAD</p>
        <span class="opd-badge">🏢 Badan Keuangan dan Aset Daerah (BKAD)</span>
    </div>
    """, unsafe_allow_html=True)

    data_path = get_data_path()

    # ── Tab: Tambah / Edit / Hapus ──
    tab_add, tab_edit, tab_delete, tab_upload = st.tabs([
        "➕ Tambah Data", "✏️ Edit Data", "🗑️ Hapus Data", "📁 Upload Excel"
    ])

    # ──────────────────────────────────────────────────────────────────────
    # TAB: TAMBAH DATA
    # ──────────────────────────────────────────────────────────────────────
    with tab_add:
        st.markdown('<div class="section-header">➕ Tambah Data Anggaran Baru</div>', unsafe_allow_html=True)

        # Session state initialization for money formatting
        if st.session_state.get("reset_tambah_inputs", False):
            st.session_state["pagu_raw_key"] = "0"
            st.session_state["realisasi_raw_key"] = "0"
            st.session_state["reset_tambah_inputs"] = False

        if "pagu_raw_key" not in st.session_state:
            st.session_state["pagu_raw_key"] = "0"
        if "realisasi_raw_key" not in st.session_state:
            st.session_state["realisasi_raw_key"] = "0"

        def _on_pagu_change():
            val = st.session_state.get("pagu_raw_key", "")
            num = parse_rupiah_input(val)
            st.session_state["pagu_raw_key"] = format_rupiah_titik(num) if num > 0 else "0"

        def _on_realisasi_change():
            val = st.session_state.get("realisasi_raw_key", "")
            num = parse_rupiah_input(val)
            st.session_state["realisasi_raw_key"] = format_rupiah_titik(num) if num > 0 else "0"

        col1, col2 = st.columns(2)
        available_jenis = get_all_jenis_belanja(data_path)
        custom_option_label = "➕ Tambah Jenis Belanja Baru (Ketik Manual)"

        with col1:
            input_tahun = st.number_input(
                "📅 Tahun Anggaran",
                min_value=2020,
                max_value=2030,
                value=2025,
                step=1,
                format="%d",
            )
            input_jenis_select = st.selectbox(
                "💰 Jenis Belanja",
                options=available_jenis + [custom_option_label],
                help="Pilih jenis belanja yang sudah ada atau pilih opsi paling bawah untuk menambah jenis belanja baru",
            )
            input_jenis_custom = st.text_input(
                "✏️ Nama Jenis Belanja Baru (Jika pilih manual)",
                placeholder="Contoh: Belanja Operasional Lainnya",
                help="Isi bidang ini hanya jika Anda memilih '➕ Tambah Jenis Belanja Baru (Ketik Manual)' di atas",
            )
            input_bulan = st.selectbox(
                "📆 Bulan",
                options=list(range(1, 13)),
                format_func=lambda x: f"{x} - {NAMA_BULAN[x]}",
            )

        with col2:
            available_pj = get_all_penanggungjawab(data_path)
            input_pj = st.selectbox(
                "🏢 Bidang Penanggung Jawab",
                options=available_pj,
            )
            input_kode = st.text_input(
                "🔢 Kode Rekening (SIPD)",
                placeholder="Contoh: 5.02.01.2.01.0001",
                help="Kode rekening SIPD/SIMDA (opsional)",
            )
            st.text_input(
                "💰 Pagu Anggaran (Rp)",
                key="pagu_raw_key",
                on_change=_on_pagu_change,
                help="Ketik nominal plafon pagu anggaran (contoh: 100000000), titik pemisah ribuan akan otomatis terformat",
                placeholder="Contoh: 100.000.000 atau 100000000",
            )
            st.text_input(
                "✅ Realisasi (Rp)",
                key="realisasi_raw_key",
                on_change=_on_realisasi_change,
                help="Ketik nominal (contoh: 500000), titik pemisah ribuan (500.000) akan otomatis terformat di dalam kotak",
                placeholder="Contoh: 500.000 atau 500000",
            )

        st.markdown("")
        if st.button("💾 Simpan Data Baru", use_container_width=True, type="primary"):
            parsed_pagu = parse_rupiah_input(st.session_state.get("pagu_raw_key", "0"))
            parsed_realisasi = parse_rupiah_input(st.session_state.get("realisasi_raw_key", "0"))

            if input_jenis_select == custom_option_label:
                final_jenis = input_jenis_custom.strip()
            else:
                final_jenis = input_jenis_select

            if not final_jenis:
                st.error("❌ Nama Jenis Belanja tidak boleh kosong. Silakan ketik nama jenis belanja baru.")
            elif parsed_pagu == 0:
                st.error("❌ Pagu Anggaran tidak boleh 0.")
            elif parsed_realisasi > parsed_pagu:
                st.warning("⚠️ Realisasi melebihi Pagu Anggaran. Pastikan data sudah benar.")
            else:
                try:
                    add_record(
                        tahun=input_tahun,
                        jenis_belanja=final_jenis,
                        bulan=input_bulan,
                        pagu_anggaran=parsed_pagu,
                        realisasi=parsed_realisasi,
                        penanggungjawab=input_pj,
                        kode_rekening=input_kode.strip(),
                        filepath=data_path,
                    )
                    st.success(
                        f"✅ Data berhasil ditambahkan: "
                        f"{final_jenis} - {NAMA_BULAN[input_bulan]} {input_tahun} (Pagu: Rp {format_rupiah_titik(parsed_pagu)})"
                    )
                    st.session_state["reset_tambah_inputs"] = True
                    st.cache_data.clear()
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ {e}")

        # Preview data terbaru
        st.markdown('<div class="section-header">📋 Data Terkini</div>', unsafe_allow_html=True)
        current_data = load_raw_data(data_path)
        if not current_data.empty:
            st.caption(f"Total: **{len(current_data)}** baris data")
            preview = current_data.tail(10).copy()

            # Format tahun tanpa koma
            preview["tahun_str"] = pd.to_numeric(preview["tahun"], errors="coerce").fillna(2025).astype(int).astype(str)
            preview["nama_bulan"] = pd.to_numeric(preview["bulan"], errors="coerce").fillna(1).astype(int).map(NAMA_BULAN)

            if "penanggungjawab" in preview.columns:
                preview["pj_str"] = preview["penanggungjawab"].fillna("-").astype(str)
            else:
                preview["pj_str"] = "-"

            if "kode_rekening" in preview.columns:
                preview["kode_str"] = preview["kode_rekening"].fillna("-").astype(str).str.replace(r'\.0$', '', regex=True)
            else:
                preview["kode_str"] = "-"

            pagu_col = "pagu_anggaran" if "pagu_anggaran" in preview.columns else ("pagu_tahunan" if "pagu_tahunan" in preview.columns else ("pagu" if "pagu" in preview.columns else None))
            if pagu_col:
                pagu_num = pd.to_numeric(preview[pagu_col], errors="coerce").fillna(0)
            else:
                pagu_num = pd.Series(0, index=preview.index)

            if "realisasi" in preview.columns:
                real_num = pd.to_numeric(preview["realisasi"], errors="coerce").fillna(0)
            else:
                real_num = pd.Series(0, index=preview.index)

            sisa_num = pagu_num - real_num
            capaian_pct = (real_num / pagu_num.replace(0, 1) * 100).round(2)

            preview["pagu_fmt"] = pagu_num.apply(lambda v: f"Rp {format_rupiah_titik(v)}")
            preview["realisasi_fmt"] = real_num.apply(lambda v: f"Rp {format_rupiah_titik(v)}")
            preview["sisa_fmt"] = sisa_num.apply(lambda v: f"Rp {format_rupiah_titik(v)}")
            preview["capaian_fmt"] = capaian_pct.apply(lambda v: f"{v:.2f}%")

            cols_preview = ["tahun_str", "pj_str", "kode_str", "jenis_belanja", "nama_bulan", "pagu_fmt", "realisasi_fmt", "sisa_fmt", "capaian_fmt"]
            st.dataframe(
                preview[cols_preview].rename(columns={
                    "tahun_str": "Tahun",
                    "pj_str": "Penanggung Jawab",
                    "kode_str": "Kode Rekening",
                    "jenis_belanja": "Jenis Belanja",
                    "nama_bulan": "Bulan",
                    "pagu_fmt": "Pagu Anggaran",
                    "realisasi_fmt": "Realisasi",
                    "sisa_fmt": "Sisa Anggaran",
                    "capaian_fmt": "% Capaian",
                }),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Tahun": st.column_config.TextColumn("Tahun"),
                    "% Capaian": st.column_config.TextColumn("% Capaian"),
                }
            )
        else:
            st.info("📭 Belum ada data. Tambahkan data melalui form di atas.")

    # ──────────────────────────────────────────────────────────────────────
    # TAB: EDIT DATA
    # ──────────────────────────────────────────────────────────────────────
    with tab_edit:
        st.markdown('<div class="section-header">✏️ Edit Data Anggaran</div>', unsafe_allow_html=True)
        st.caption("Edit langsung di tabel di bawah ini, lalu klik **💾 Simpan Perubahan**.")

        edit_data = load_raw_data(data_path)

        if edit_data.empty:
            st.info("📭 Belum ada data untuk diedit.")
        else:
            # Filter untuk mempersempit data yang diedit
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                edit_tahun = st.selectbox(
                    "Filter Tahun",
                    options=["Semua"] + safe_sorted_years(edit_data["tahun"]),
                    key="edit_filter_tahun",
                )
            with col_f2:
                edit_jenis = st.selectbox(
                    "Filter Jenis Belanja",
                    options=["Semua"] + safe_sorted_options(edit_data["jenis_belanja"]),
                    key="edit_filter_jenis",
                )

            # Apply filter
            filtered_edit = edit_data.copy()
            if edit_tahun != "Semua":
                filtered_edit = filtered_edit[pd.to_numeric(filtered_edit["tahun"], errors="coerce") == edit_tahun]
            if edit_jenis != "Semua":
                filtered_edit = filtered_edit[filtered_edit["jenis_belanja"].astype(str).str.strip() == edit_jenis]

            if filtered_edit.empty:
                st.warning("⚠️ Tidak ada data sesuai filter.")
            else:
                st.caption(f"Menampilkan **{len(filtered_edit)}** baris data")

                # Format angka ke string berpemisah titik dan bersihkan tipe data untuk tabel editor
                display_edit = filtered_edit.copy()
                if "tahun" in display_edit.columns:
                    display_edit["tahun"] = pd.to_numeric(display_edit["tahun"], errors="coerce").fillna(2024).astype(int)
                if "bulan" in display_edit.columns:
                    display_edit["bulan"] = pd.to_numeric(display_edit["bulan"], errors="coerce").fillna(1).astype(int)
                if "nama_opd" in display_edit.columns:
                    display_edit["nama_opd"] = display_edit["nama_opd"].fillna("").astype(str)
                if "penanggungjawab" in display_edit.columns:
                    display_edit["penanggungjawab"] = display_edit["penanggungjawab"].fillna("Sekretariat").astype(str)
                if "kode_rekening" in display_edit.columns:
                    display_edit["kode_rekening"] = display_edit["kode_rekening"].fillna("").astype(str).str.replace(r'\.0$', '', regex=True)
                if "jenis_belanja" in display_edit.columns:
                    display_edit["jenis_belanja"] = display_edit["jenis_belanja"].fillna("").astype(str)
                if "pagu_anggaran" in display_edit.columns:
                    display_edit["pagu_anggaran"] = display_edit["pagu_anggaran"].apply(format_rupiah_titik)
                if "realisasi" in display_edit.columns:
                    display_edit["realisasi"] = display_edit["realisasi"].apply(format_rupiah_titik)

                pj_options = get_all_penanggungjawab(data_path)
                if "penanggungjawab" in display_edit.columns:
                    current_pjs = [str(x) for x in display_edit["penanggungjawab"].unique() if str(x).strip()]
                    for pj in current_pjs:
                        if pj not in pj_options:
                            pj_options.append(pj)

                edit_cols = [c for c in ["tahun", "nama_opd", "penanggungjawab", "kode_rekening", "jenis_belanja", "bulan", "pagu_anggaran", "realisasi"] if c in display_edit.columns]
                edited_df = st.data_editor(
                    display_edit[edit_cols],
                    column_config={
                        "tahun": st.column_config.NumberColumn("Tahun", min_value=2020, max_value=2030, format="%d"),
                        "nama_opd": st.column_config.TextColumn("Nama OPD", disabled=True),
                        "penanggungjawab": st.column_config.SelectboxColumn("Penanggung Jawab", options=pj_options),
                        "kode_rekening": st.column_config.TextColumn("Kode Rekening"),
                        "jenis_belanja": st.column_config.TextColumn("Sub-Kegiatan / Uraian"),
                        "bulan": st.column_config.NumberColumn("Bulan", min_value=1, max_value=12, format="%d"),
                        "pagu_anggaran": st.column_config.TextColumn("Pagu Anggaran (Rp)", help="Format dengan pemisah titik (contoh: 1.000.000)"),
                        "realisasi": st.column_config.TextColumn("Realisasi (Rp)", help="Format dengan pemisah titik (contoh: 500.000)"),
                    },
                    use_container_width=True,
                    hide_index=False,
                    num_rows="fixed",
                    key="data_editor",
                )

                st.markdown("")
                if st.button("💾 Simpan Perubahan", use_container_width=True, type="primary"):
                    try:
                        # Update data asli dengan data yang diedit
                        full_data = load_raw_data(data_path)

                        # Update baris yang diedit (gunakan index asli)
                        for idx in edited_df.index:
                            for col in ["tahun", "penanggungjawab", "kode_rekening", "jenis_belanja", "bulan"]:
                                if col in edited_df.columns:
                                    full_data.at[idx, col] = edited_df.at[idx, col]
                            if "pagu_anggaran" in edited_df.columns:
                                full_data.at[idx, "pagu_anggaran"] = parse_rupiah_input(str(edited_df.at[idx, "pagu_anggaran"]))
                            if "realisasi" in edited_df.columns:
                                full_data.at[idx, "realisasi"] = parse_rupiah_input(str(edited_df.at[idx, "realisasi"]))

                        bulk_save(full_data, data_path)
                        st.success("✅ Perubahan berhasil disimpan!")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Gagal menyimpan: {e}")

    # ──────────────────────────────────────────────────────────────────────
    # TAB: HAPUS DATA
    # ──────────────────────────────────────────────────────────────────────
    with tab_delete:
        st.markdown('<div class="section-header">🗑️ Hapus Data Anggaran</div>', unsafe_allow_html=True)

        with st.expander("🚨 Zona Bahaya: Kosongkan Seluruh Database (Google Sheets & Lokal)", expanded=False):
            st.warning("⚠️ Tombol ini akan menghapus **SELURUH DATA** yang ada di Google Sheets dan Lokal hingga 100% kosong.")
            if st.button("💣 KOSONGKAN SELURUH DATABASE SEKARANG", type="primary", key="btn_wipe_all_db"):
                empty_cols = ["tahun", "nama_opd", "penanggungjawab", "kode_rekening", "jenis_belanja", "bulan", "pagu_anggaran", "realisasi"]
                empty_df = pd.DataFrame(columns=empty_cols)
                save_data(empty_df, data_path)
                st.cache_data.clear()
                st.success("✅ Seluruh data di Google Sheets & lokal telah dikosongkan!")
                st.rerun()

        del_data = load_raw_data(data_path)

        if del_data.empty:
            st.info("📭 Belum ada data.")
        else:
            # Filter
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                del_tahun = st.selectbox(
                    "Filter Tahun",
                    options=["Semua"] + safe_sorted_years(del_data["tahun"]),
                    key="del_filter_tahun",
                )
            with col_d2:
                del_jenis = st.selectbox(
                    "Filter Jenis Belanja",
                    options=["Semua"] + safe_sorted_options(del_data["jenis_belanja"]),
                    key="del_filter_jenis",
                )

            filtered_del = del_data.copy()
            if del_tahun != "Semua":
                filtered_del = filtered_del[pd.to_numeric(filtered_del["tahun"], errors="coerce") == del_tahun]
            if del_jenis != "Semua":
                filtered_del = filtered_del[filtered_del["jenis_belanja"].astype(str).str.strip() == del_jenis]

            if filtered_del.empty:
                st.warning("⚠️ Tidak ada data sesuai filter.")
            else:
                # Tampilkan data dengan checkbox/editor
                display_del = filtered_del.copy()
                display_del["tahun_str"] = pd.to_numeric(display_del["tahun"], errors="coerce").fillna(2025).astype(int).astype(str)

                if "bulan" in display_del.columns:
                    display_del["bulan_num"] = pd.to_numeric(display_del["bulan"], errors="coerce").fillna(1).astype(int)
                    display_del["nama_bulan"] = display_del["bulan_num"].map(NAMA_BULAN)
                else:
                    display_del["nama_bulan"] = "-"

                if "penanggungjawab" in display_del.columns:
                    display_del["pj_str"] = display_del["penanggungjawab"].fillna("-").astype(str)
                else:
                    display_del["pj_str"] = "-"

                if "kode_rekening" in display_del.columns:
                    display_del["kode_str"] = display_del["kode_rekening"].fillna("-").astype(str).str.replace(r'\.0$', '', regex=True)
                else:
                    display_del["kode_str"] = "-"

                pagu_num = pd.to_numeric(display_del["pagu_anggaran"], errors="coerce").fillna(0) if "pagu_anggaran" in display_del.columns else pd.Series(0, index=display_del.index)
                real_num = pd.to_numeric(display_del["realisasi"], errors="coerce").fillna(0) if "realisasi" in display_del.columns else pd.Series(0, index=display_del.index)
                sisa_num = pagu_num - real_num
                capaian_pct = (real_num / pagu_num.replace(0, 1) * 100).round(2)

                display_del["pagu_fmt"] = pagu_num.apply(lambda v: f"Rp {format_rupiah_titik(v)}")
                display_del["realisasi_fmt"] = real_num.apply(lambda v: f"Rp {format_rupiah_titik(v)}")
                display_del["sisa_fmt"] = sisa_num.apply(lambda v: f"Rp {format_rupiah_titik(v)}")
                display_del["capaian_fmt"] = capaian_pct.apply(lambda v: f"{v:.2f}%")

                cols_del = ["tahun_str", "pj_str", "kode_str", "jenis_belanja", "nama_bulan", "pagu_fmt", "realisasi_fmt", "sisa_fmt", "capaian_fmt"]
                cols_rename = {
                    "tahun_str": "Tahun",
                    "pj_str": "Penanggung Jawab",
                    "kode_str": "Kode Rekening",
                    "jenis_belanja": "Jenis Belanja",
                    "nama_bulan": "Bulan",
                    "pagu_fmt": "Pagu Anggaran",
                    "realisasi_fmt": "Realisasi",
                    "sisa_fmt": "Sisa Anggaran",
                    "capaian_fmt": "% Capaian",
                }
                selected_del = st.data_editor(
                    display_del[cols_del].rename(columns=cols_rename),
                    use_container_width=True,
                    hide_index=False,
                    num_rows="fixed",
                    key="delete_selector",
                    disabled=list(cols_rename.values()),
                )

                st.markdown("")

                # Hapus berdasarkan pilihan index
                col_del_btn1, col_del_btn2 = st.columns(2)

                with col_del_btn1:
                    # Hapus semua data yang terfilter
                    if st.button("🗑️ Hapus Semua Data Terfilter", use_container_width=True, type="secondary"):
                        st.session_state["confirm_delete_all"] = True

                with col_del_btn2:
                    # Hapus per baris (input index)
                    del_indices_input = st.text_input(
                        "Masukkan nomor baris yang akan dihapus (pisah koma)",
                        placeholder="contoh: 0, 1, 5",
                        key="del_indices_input",
                    )

                # Konfirmasi hapus semua
                if st.session_state.get("confirm_delete_all", False):
                    st.warning(f"⚠️ Anda akan menghapus **{len(filtered_del)} baris** data. Tindakan ini tidak bisa dibatalkan!")
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        if st.button("✅ Ya, Hapus Semua", type="primary", use_container_width=True):
                            try:
                                delete_records(filtered_del.index.tolist(), data_path)
                                st.success(f"✅ {len(filtered_del)} baris data berhasil dihapus!")
                                st.cache_data.clear()
                                st.session_state["confirm_delete_all"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Gagal menghapus: {e}")
                    with col_c2:
                        if st.button("❌ Batal", use_container_width=True):
                            st.session_state["confirm_delete_all"] = False
                            st.rerun()

                # Hapus per index
                if del_indices_input:
                    if st.button("🗑️ Hapus Baris Terpilih", type="primary", use_container_width=True):
                        try:
                            indices = [int(i.strip()) for i in del_indices_input.split(",")]
                            # Validasi index
                            valid_indices = [i for i in indices if i in filtered_del.index]
                            if not valid_indices:
                                st.error("❌ Index tidak valid. Gunakan nomor baris yang terlihat di tabel.")
                            else:
                                delete_records(valid_indices, data_path)
                                st.success(f"✅ {len(valid_indices)} baris data berhasil dihapus!")
                                st.cache_data.clear()
                                st.rerun()
                        except ValueError:
                            st.error("❌ Format index salah. Gunakan angka yang dipisah koma, contoh: 0, 1, 5")

    # ──────────────────────────────────────────────────────────────────────
    # TAB: UPLOAD EXCEL
    # ──────────────────────────────────────────────────────────────────────
    with tab_upload:
        st.markdown('<div class="section-header">📁 Upload File Excel</div>', unsafe_allow_html=True)
        st.caption(
            "Upload file Excel untuk **mengganti seluruh data** yang ada. "
            "File harus memiliki kolom: `tahun`, `nama_opd`, `jenis_belanja`, `bulan`, `pagu_anggaran`, `realisasi`."
        )

        # Download template
        template_path = os.path.join(os.path.dirname(__file__), "data", "template_upload.xlsx")
        if os.path.exists(template_path):
            with open(template_path, "rb") as f:
                st.download_button(
                    label="📥 Download Template Excel",
                    data=f.read(),
                    file_name="template_realisasi_anggaran.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    help="Download template Excel yang sudah diformat. Isi data Anda lalu upload kembali.",
                )
            st.markdown("")

        upload_mode = st.radio(
            "Pilih Mode Upload Data:",
            options=[
                "🔄 Perbarui & Tambah Data (Merge/Upsert - Memperbarui data yang ada dan menambah data baru)",
                "💥 Ganti Seluruh Data (Replace All - Menghapus seluruh database lama)",
            ],
            index=0,
            help="Mode 1: Memperbarui data yang cocok & menambahkan data baru tanpa menghapus data lama.\nMode 2: Menghapus seluruh isi database lama secara permanen.",
        )

        upload_file = st.file_uploader(
            "Pilih file Excel",
            type=["xlsx", "xls"],
            key="upload_replace",
        )

        if upload_file is not None:
            try:
                raw_df = read_smart_excel(upload_file)
                preview_df, upload_warnings = validate_and_sanitize_excel(raw_df)

                for w in upload_warnings:
                    st.warning(f"⚠️ {w}")

                display_upload = preview_df.head(20).copy()
                if "tahun" in display_upload.columns:
                    display_upload["tahun"] = pd.to_numeric(display_upload["tahun"], errors="coerce").fillna(2025).astype(int).astype(str)

                st.markdown("### Preview Data (20 Baris Pertama)")
                st.dataframe(
                    display_upload,
                    use_container_width=True,
                    hide_index=True,
                    column_config={"tahun": st.column_config.TextColumn("tahun")},
                )
                st.caption(f"Total baris valid: **{len(preview_df)}**")

                required = ["tahun", "nama_opd", "jenis_belanja", "bulan", "pagu_anggaran", "realisasi"]
                missing = [c for c in required if c not in preview_df.columns]

                if missing:
                    st.error(f"❌ Kolom tidak lengkap. Kolom yang hilang: {', '.join(missing)}")
                else:
                    st.success("✅ Format file valid & siap disimpan!")
                    if "🔄" in upload_mode:
                        btn_label = "💾 Perbarui & Tambahkan Data Baru"
                    else:
                        btn_label = "💥 Ganti Seluruh Data dengan File Ini"

                    if st.button(btn_label, type="primary", use_container_width=True):
                        if "🔄" in upload_mode:
                            n_rows = merge_save_records(preview_df, data_path)
                            st.success(f"✅ Berhasil memperbarui & menggabungkan {n_rows} baris data!")
                        else:
                            bulk_save(preview_df, data_path)
                            st.success("✅ Seluruh data lama berhasil diganti!")

                        st.cache_data.clear()
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Error membaca file: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📊 Dashboard":

    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard Realisasi Anggaran</h1>
        <p>Visualisasi interaktif data realisasi anggaran</p>
        <span class="opd-badge">🏢 Badan Keuangan dan Aset Daerah (BKAD)</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar Filters ──
    with st.sidebar:
        data_path = get_data_path()
        df = load_data(data_path)
        data_source = "📊 Google Sheets" if is_gsheets_configured() else "📄 Data Database / Lokal"

        if df is None or df.empty:
            st.info("💡 Belum ada data anggaran. Silakan login ke menu Kelola Data untuk menginput/mengupload data.")
            st.stop()

        st.caption(f"Sumber Data: {data_source}")
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        st.markdown("## 🔍 Filter")

        tahun_options = safe_sorted_years(df["tahun"])
        selected_tahun = st.selectbox(
            "📅 Tahun Anggaran",
            options=tahun_options,
            index=len(tahun_options) - 1,
        )

        pj_options = safe_sorted_options(df["penanggungjawab"]) if "penanggungjawab" in df.columns else []
        selected_pj = st.multiselect(
            "🏢 Bidang Penanggung Jawab",
            options=pj_options,
            default=[],
            placeholder="Semua Bidang",
        ) if pj_options else []

        belanja_options = safe_sorted_options(df["jenis_belanja"])
        selected_belanja = st.multiselect(
            "💰 Sub-Kegiatan / Jenis Belanja",
            options=belanja_options,
            default=[],
            placeholder="Semua Sub-Kegiatan",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        st.markdown("## ℹ️ Informasi")
        st.caption(f"Total baris data: **{len(df):,}**")
        if pj_options:
            st.caption(f"Jumlah Bidang: **{len(pj_options)}**")
        st.caption(f"Jumlah Sub-Kegiatan: **{df['jenis_belanja'].nunique()}**")
        st.caption(f"Tahun tersedia: **{', '.join(map(str, tahun_options))}**")

    # ── Apply Filters ──
    df_filtered = filter_data(
        df,
        tahun=selected_tahun,
        penanggungjawab_list=selected_pj if selected_pj else None,
        jenis_belanja_list=selected_belanja if selected_belanja else None,
    )

    if df_filtered.empty:
        st.warning("⚠️ Tidak ada data sesuai filter. Coba ubah filter di sidebar.")
        st.stop()

    # ── Summary Metrics ──
    summary = get_summary(df_filtered)
    latest_bln_name = NAMA_BULAN.get(summary.get("latest_bulan", 1), "")

    # ── Executive Summary & Insight Card ──
    insights = get_executive_insights(df_filtered, summary)
    with st.expander("💡 Executive Summary & Insight Naratif Otomatis", expanded=True):
        st.markdown("#### 📌 Ringkasan Eksekutif & Analisis Data")
        for b in insights["bullets"]:
            st.markdown(f"- {b}")

    st.markdown("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">💰 Total Pagu Tahunan</div>
            <div class="metric-value blue">{format_rupiah(summary['total_pagu'])}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">✅ Total Realisasi</div>
            <div class="metric-value green">{format_rupiah(summary['total_realisasi'])}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📉 Sisa Pagu Tahunan</div>
            <div class="metric-value red">{format_rupiah(summary['total_sisa'])}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        pct = summary['persentase']
        if pct >= 80:
            badge_class = "status-good"
            badge_text = "Baik"
        elif pct >= 50:
            badge_class = "status-warning"
            badge_text = "Cukup"
        else:
            badge_class = "status-danger"
            badge_text = "Rendah"

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">📊 Persentase Realisasi ({latest_bln_name})</div>
            <div class="metric-value orange">{pct:.2f}%</div>
            <span class="status-badge {badge_class}">{badge_text}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # ── Gauge + Trend ──
    col_gauge, col_trend = st.columns([1, 2.5])

    with col_gauge:
        st.markdown('<div class="section-header">🎯 Capaian Realisasi</div>', unsafe_allow_html=True)
        gauge_fig = create_gauge_chart(summary["persentase"])
        st.plotly_chart(gauge_fig, use_container_width=True, config={"displayModeBar": False})

    with col_trend:
        st.markdown('<div class="section-header">📈 Tren Realisasi</div>', unsafe_allow_html=True)
        trend_tab1, trend_tab2 = st.tabs(["📅 Bulanan", "📊 Triwulanan"])

        with trend_tab1:
            monthly = get_monthly_trend(df_filtered)
            trend_fig = create_trend_chart(monthly, mode="bulanan")
            st.plotly_chart(trend_fig, use_container_width=True, config={"displayModeBar": False})

        with trend_tab2:
            quarterly = get_quarterly_trend(df_filtered)
            trend_fig_q = create_trend_chart(quarterly, mode="triwulanan")
            st.plotly_chart(trend_fig_q, use_container_width=True, config={"displayModeBar": False})

    # ── Penanggung Jawab Comparison ──
    if "penanggungjawab" in df_filtered.columns:
        pj_comp = get_pj_comparison(df_filtered)
        if not pj_comp.empty:
            st.markdown('<div class="section-header">🏢 Capaian Realisasi per Bidang Penanggung Jawab</div>', unsafe_allow_html=True)
            pj_fig = create_pj_comparison(pj_comp)
            st.plotly_chart(pj_fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── Belanja Comparison + Composition ──
    col_bar, col_donut = st.columns([2, 1])

    with col_bar:
        st.markdown('<div class="section-header">📊 Perbandingan per Jenis Belanja</div>', unsafe_allow_html=True)
        belanja_comparison = get_belanja_comparison(df_filtered)
        bar_fig = create_belanja_comparison(belanja_comparison)
        st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})

    with col_donut:
        st.markdown('<div class="section-header">🥧 Komposisi Belanja</div>', unsafe_allow_html=True)
        composition = get_belanja_composition(df_filtered)
        donut_fig = create_donut_chart(composition)
        st.plotly_chart(donut_fig, use_container_width=True, config={"displayModeBar": False})

    # ── Heatmap ──
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">🗓️ Heatmap Realisasi per Jenis Belanja per Bulan</div>', unsafe_allow_html=True)

    heatmap_fig = create_heatmap_belanja_monthly(df_filtered)
    st.plotly_chart(heatmap_fig, use_container_width=True, config={"displayModeBar": False})

    # ── Detail Table ──
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📋 Tabel Detail Realisasi Sub-Kegiatan BKAD</div>', unsafe_allow_html=True)

    group_cols = ["jenis_belanja"]
    if "penanggungjawab" in df_filtered.columns:
        group_cols.insert(0, "penanggungjawab")
    if "kode_rekening" in df_filtered.columns:
        group_cols.insert(0, "kode_rekening")

    idx = df_filtered.groupby(group_cols, dropna=False)["bulan"].idxmax()
    latest_detail = df_filtered.loc[idx].copy()

    # Search filter
    col_search1, _ = st.columns([2, 1])
    with col_search1:
        search_query = st.text_input(
            "🔍 Cari Sub-Kegiatan / Kode Rekening / Bidang...",
            placeholder="Ketik nama sub-kegiatan, kode rekening, atau bidang...",
            key="dashboard_search_input",
        ).strip().lower()

    if search_query:
        mask = latest_detail["jenis_belanja"].astype(str).str.lower().str.contains(search_query)
        if "kode_rekening" in latest_detail.columns:
            mask = mask | latest_detail["kode_rekening"].astype(str).str.lower().str.contains(search_query)
        if "penanggungjawab" in latest_detail.columns:
            mask = mask | latest_detail["penanggungjawab"].astype(str).str.lower().str.contains(search_query)
        latest_detail = latest_detail[mask]
        st.caption(f"Pencarian Cepat: Menampilkan **{len(latest_detail)}** sub-kegiatan yang cocok.")

    real_col = "realisasi_kumulatif" if "realisasi_kumulatif" in latest_detail.columns else "realisasi"
    latest_detail["sisa"] = latest_detail["pagu_anggaran"] - latest_detail[real_col]
    latest_detail["persentase"] = (
        (latest_detail[real_col] / latest_detail["pagu_anggaran"].replace(0, 1) * 100)
        .round(2)
        .fillna(0)
    )

    latest_detail = latest_detail.sort_values("pagu_anggaran", ascending=False)

    latest_detail["pagu_fmt"] = latest_detail["pagu_anggaran"].apply(format_rupiah)
    latest_detail["realisasi_fmt"] = latest_detail[real_col].apply(format_rupiah)
    latest_detail["sisa_fmt"] = latest_detail["sisa"].apply(format_rupiah)
    latest_detail["persentase_fmt"] = latest_detail["persentase"].apply(lambda x: f"{x:.2f}%")

    cols_to_show = []
    col_rename = {}

    if "kode_rekening" in latest_detail.columns:
        cols_to_show.append("kode_rekening")
        col_rename["kode_rekening"] = "Kode Rekening"

    if "penanggungjawab" in latest_detail.columns:
        cols_to_show.append("penanggungjawab")
        col_rename["penanggungjawab"] = "Penanggung Jawab"

    cols_to_show.extend(["jenis_belanja", "pagu_fmt", "realisasi_fmt", "sisa_fmt", "persentase_fmt"])
    col_rename.update({
        "jenis_belanja": "Sub-Kegiatan / Uraian",
        "pagu_fmt": "Pagu Anggaran",
        "realisasi_fmt": "Realisasi (Kumulatif)",
        "sisa_fmt": "Sisa Anggaran",
        "persentase_fmt": "% Capaian",
    })

    display_table = latest_detail[cols_to_show].rename(columns=col_rename)

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True,
        height=min(450, len(display_table) * 38 + 50),
    )

    # ── Download ──
    st.markdown("")
    col_dl1, col_dl2, col_dl3 = st.columns([1.5, 1.5, 1])

    with col_dl1:
        try:
            excel_report_bytes = generate_formatted_excel_report(df_filtered, summary, selected_tahun)
            st.download_button(
                label="📊 Download Laporan Excel",
                data=excel_report_bytes,
                file_name=f"laporan_realisasi_bkad_{selected_tahun}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"❌ Gagal membuat Laporan Excel: {e}")

    with col_dl2:
        try:
            pdf_report_bytes = generate_formatted_pdf_report(df_filtered, summary, selected_tahun)
            st.download_button(
                label="📄 Download Laporan PDF",
                data=pdf_report_bytes,
                file_name=f"laporan_realisasi_bkad_{selected_tahun}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"❌ Gagal membuat Laporan PDF: {e}")

    with col_dl3:
        csv_summary = latest_detail.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Data CSV",
            data=csv_summary,
            file_name=f"ringkasan_bkad_{selected_tahun}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col_dl3:
        csv_data = df_filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Data Mentah (CSV)",
            data=csv_data,
            file_name=f"realisasi_bkad_{selected_tahun}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.caption(
        "📊 Dashboard Realisasi Anggaran BKAD | "
        "Dibuat dengan Streamlit & Plotly | "
        f"Data tahun {selected_tahun}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PANDUAN (MANUAL BOOK)
# ═══════════════════════════════════════════════════════════════════════════════

elif page == "📖 Panduan":

    st.markdown("""
    <div class="main-header">
        <h1>📖 Panduan Penggunaan Dashboard BKAD</h1>
        <p>Dokumentasi dan petunjuk penggunaan aplikasi realisasi anggaran</p>
        <span class="opd-badge">🏢 Badan Keuangan dan Aset Daerah (BKAD)</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Daftar Isi ──
    st.markdown("""
    <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 1.2rem; margin-bottom: 1.5rem;">
        <h4 style="margin-top:0; color: #3498DB;">📌 Daftar Isi</h4>
        <ol style="margin-bottom:0; color: #FAFAFA; font-size: 0.95rem; line-height: 1.8;">
            <li><a href="#1-tentang-aplikasi" style="color: #2ECC71; text-decoration: none;">Tentang Aplikasi & Sistem Otorisasi</a></li>
            <li><a href="#2-halaman-dashboard" style="color: #2ECC71; text-decoration: none;">Halaman Dashboard & Visualisasi</a></li>
            <li><a href="#3-kelola-data" style="color: #2ECC71; text-decoration: none;">Kelola Data (Tambah, Edit, Hapus, Upload)</a></li>
            <li><a href="#4-template-upload-data" style="color: #2ECC71; text-decoration: none;">Template Upload Excel (SIPD)</a></li>
            <li><a href="#5-struktur-data" style="color: #2ECC71; text-decoration: none;">Struktur Data & Format Ribuan</a></li>
            <li><a href="#6-faq-troubleshooting" style="color: #2ECC71; text-decoration: none;">FAQ & Troubleshooting</a></li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 1: TENTANG APLIKASI
    # ──────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header" id="1-tentang-aplikasi">1️⃣ Tentang Aplikasi & Sistem Otorisasi</div>', unsafe_allow_html=True)

    st.markdown("""
    Aplikasi ini dirancang khusus untuk memvisualisasikan dan mengelola **Data Realisasi Anggaran Badan Keuangan dan Aset Daerah (BKAD)** secara interaktif, akurat, dan real-time.

    #### 🛡️ Hak Akses & Otorisasi Pengguna:
    Untuk menjaga keamanan data anggaran, aplikasi membagi hak akses menjadi **2 Tingkatan**:

    | Tingkat Akses | Hak Akses | Fitur yang Dapat Diakses |
    |---------------|-----------|--------------------------|
    | 🌐 **Publik (Tamu)** | Read-Only | Merekap & melihat visualisasi **Dashboard** serta membaca **Panduan**. |
    | 🔐 **Admin BKAD** | Full Access (CRUD) | Melakukan Tambah, Edit, Hapus data, serta Upload file Excel di halaman **Kelola Data**. |

    💡 *Untuk mendapatkan akses akun Admin pengelola data, silakan hubungi Administrator Sistem BKAD.*
    """)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 2: DASHBOARD
    # ──────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header" id="2-halaman-dashboard">2️⃣ Halaman Dashboard</div>', unsafe_allow_html=True)

    with st.expander("🔍 Filter Sidebar", expanded=True):
        st.markdown("""
        Sidebar sebelah kiri menyediakan 3 filter utama:
        - 📅 **Tahun Anggaran** — Memilih tahun realisasi (misal: 2025)
        - 🏢 **Bidang Penanggung Jawab** — Memilih 1 atau beberapa bidang (Sekretariat, Bidang Anggaran, Bidang Perbendaharaan, Bidang Akuntansi & Pelaporan, Bidang Pengelolaan BMD)
        - 💰 **Sub-Kegiatan / Uraian** — Memilih sub-kegiatan tertentu
        """)

    with st.expander("📊 Kartu Ringkasan (Metric Cards)", expanded=False):
        st.markdown("""
        Menampilkan 4 indikator utama:
        - **💰 Total Pagu Anggaran** — Ditulis dalam format Rupiah penuh (misal: `Rp 366.999.332.784`)
        - **✅ Total Realisasi** — Ditulis dalam format Rupiah penuh (misal: `Rp 105.107.575.969`)
        - **📉 Sisa Anggaran** — Pagu dikurangi realisasi
        - **📊 Persentase Realisasi** — Persentase capaian + indikator status (🟢 Baik ≥80%, 🟡 Cukup 50-79%, 🔴 Rendah <50%)
        """)

    with st.expander("🏢 Grafik per Bidang & Sub-Kegiatan", expanded=False):
        st.markdown("""
        - **Capaian per Bidang Penanggung Jawab** — Horizontal bar chart perbandingan Pagu vs Realisasi per bidang.
        - **Perbandingan per Sub-Kegiatan** — Horizontal bar chart perbandingan Pagu vs Realisasi 79 sub-kegiatan BKAD.
        - **Donut Chart & Heatmap** — Proporsi realisasi dan peta warna intensitas realisasi bulanan.
        """)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 3: KELOLA DATA
    # ──────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header" id="3-kelola-data">3️⃣ Kelola Data (CRUD)</div>', unsafe_allow_html=True)

    with st.expander("➕ Form Tambah Data (Auto-Format Titik)", expanded=True):
        st.markdown("""
        **Langkah-langkah:**
        1. Pilih menu **📝 Kelola Data** di sidebar kiri.
        2. Masukkan **Username & Password Admin** jika belum login.
        3. Pada tab **➕ Tambah Data**, isi form:
           - 📅 **Tahun Anggaran** & 📆 **Bulan**
           - 🏢 **Bidang Penanggung Jawab** — Pilih dari list bidang
           - 🔢 **Kode Rekening** — Masukkan kode SIPD (misal: `5.02.01.2.01.0001`)
           - 💰 **Sub-Kegiatan / Jenis Belanja** — Pilih dari dropdown atau pilih `"➕ Tambah Jenis Belanja Baru"`
           - 💰 **Pagu Anggaran & Realisasi** — Ketik angka biasa (misal `1000000`), saat Anda berpindah kolom, angka akan **otomatis berpemisah titik (`1.000.000`)**.
        4. Klik **💾 Simpan Data Baru**.
        """)

    with st.expander("✏️ Tab Edit Data", expanded=True):
        st.markdown("""
        **Langkah-langkah:**
        1. Buka tab **✏️ Edit Data**.
        2. Gunakan filter untuk menemukan baris data.
        3. **Klik langsung pada sel** di tabel yang ingin diubah.
        4. Nilai Pagu Anggaran & Realisasi ditampilkan dalam format titik (misal `12.310.000`). Anda dapat langsung mengetikkan perubahan nilai dengan format titik.
        5. Klik **💾 Simpan Perubahan**.
        """)

    with st.expander("🗑️ Tab Hapus Data & 📁 Upload Excel", expanded=True):
        st.markdown("""
        - **Hapus Data**: Pilih baris tertentu atau hapus data terfilter.
        - **Upload Excel**: Timpa seluruh data dengan file Excel SIPD baru.
        """)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 4: TEMPLATE UPLOAD
    # ──────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header" id="4-template-upload-data">4️⃣ Template Upload Excel (SIPD)</div>', unsafe_allow_html=True)

    template_path = os.path.join(os.path.dirname(__file__), "data", "template_upload.xlsx")
    if os.path.exists(template_path):
        with open(template_path, "rb") as f:
            st.download_button(
                label="📥 Download Template Excel (SIPD BKAD)",
                data=f.read(),
                file_name="template_realisasi_bkad.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="template_panduan_download",
            )

    st.markdown("""
    Template Excel telah disesuaikan dengan format laporan SIPD BKAD terbaru.
    - Sheet **`Data Realisasi`** (Sheet 0 / Utama) — Tempat mengisi data realisasi (telah dilengkapi 3 baris contoh).
    - Sheet **`Petunjuk Pengisian`** (Sheet 1) — Panduan lengkap aturan dan pengisian tiap kolom.

    💡 **Pembaca Cerdas Excel (Smart Sheet Reader):**
    Aplikasi secara otomatis mendeteksi sheet **`Data Realisasi`** atau sheet mana saja dalam file Excel Anda yang berisi kolom-kolom data anggaran. Anda dapat mengunggah file Excel ber-sheet banyak tanpa perlu khawatir error pembacaan!
    """)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 5: STRUKTUR DATA
    # ──────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header" id="5-struktur-data">5️⃣ Struktur Data & Format Ribuan</div>', unsafe_allow_html=True)

    st.markdown("""
    | No | Nama Kolom | Tipe Data | Keterangan | Contoh |
    |----|------------|-----------|------------|--------|
    | 1 | `tahun` | Integer | Tahun Anggaran | `2025` |
    | 2 | `nama_opd` | String | Nama OPD | `Badan Keuangan dan Aset Daerah (BKAD)` |
    | 3 | `penanggungjawab` | String | Bidang Penanggung Jawab | `Sekretariat / Bidang Anggaran` |
    | 4 | `kode_rekening` | String | Kode Rekening SIPD | `5.02.01.2.01.0001` |
    | 5 | `jenis_belanja` | String | Nama Sub-Kegiatan / Uraian | `Penyusunan Dokumen Perencanaan...` |
    | 6 | `bulan` | Integer (1-12) | Bulan Realisasi | `1` |
    | 7 | `pagu_anggaran` | Numeric | Pagu Anggaran (Rp) | `16.342.500` |
    | 8 | `realisasi` | Numeric | Realisasi Kumulatif (Rp) | `2.440.000` |

    💡 **Format Nominal Uang:**
    Seluruh nominal uang ditampilkan secara penuh **tanpa singkatan** (Jt/M) menggunakan pemisah titik sebagai penanda ribuan (misal: `Rp 2.000.000` atau `Rp 261.891.756.815`).
    """)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 6: FAQ
    # ──────────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header" id="6-faq-troubleshooting">6️⃣ FAQ & Troubleshooting</div>', unsafe_allow_html=True)

    with st.expander("❓ Siapa yang bisa mengedit data anggaran?"):
        st.markdown("Hanya pengguna terverifikasi yang telah melakukan **Login Admin** di halaman **Kelola Data**.")

    with st.expander("❓ Bagaimana cara mengetik nominal Rupiah pada form?"):
        st.markdown("Anda bisa mengetik angka biasa `1000000` atau `1.000.000`. Kotak input akan otomatis membuat titik pemisah ribuan saat Anda selesai mengetik.")

    with st.expander("❓ Bagaimana cara deploy aplikasi ini ke internet secara gratis?"):
        st.markdown("""
        1. Upload seluruh folder proyek ke repository **GitHub** Anda.
        2. Buka [streamlit.io/cloud](https://streamlit.io/cloud) dan login dengan akun GitHub Anda.
        3. Klik **New app** -> pilih repository -> tentukan `app.py` -> klik **Deploy**.
        4. Dashboard realisasi BKAD Anda akan langsung live di internet secara gratis!
        """)

    with st.expander("❓ Aplikasi error saat dijalankan?"):
        st.code("""
# Pastikan virtual environment aktif
source env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Jalankan ulang
streamlit run app.py
        """, language="bash")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.caption("📖 Panduan Dashboard Realisasi Anggaran BKAD — v1.0")
