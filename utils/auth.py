"""
Modul Otorisasi (Authentication & Authorization) untuk Halaman Kelola Data.
"""
import streamlit as st
import os

# Credential bawaan (bisa diubah via environment variable atau form)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "bkad2025")


def is_authenticated() -> bool:
    """Memeriksa apakah pengguna sudah login sebagai Admin."""
    return st.session_state.get("authenticated", False)


def login(username: str, password: str) -> bool:
    """Verifikasi username dan password."""
    if username.strip() == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        st.session_state["authenticated"] = True
        st.session_state["username"] = username.strip()
        return True
    return False


def logout() -> None:
    """Keluar dari sesi Admin."""
    st.session_state["authenticated"] = False
    st.session_state.pop("username", None)


def render_login_box() -> None:
    """Menampilkan form login yang elegan untuk halaman Kelola Data."""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(27, 40, 56, 0.9), rgba(15, 23, 42, 0.95));
        border: 1px solid rgba(52, 152, 219, 0.3);
        border-radius: 12px;
        padding: 30px;
        max-width: 480px;
        margin: 20px auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        text-align: center;
    ">
        <div style="font-size: 48px; margin-bottom: 10px;">🔒</div>
        <h2 style="color: #FAFAFA; margin-bottom: 5px; font-weight: 700;">Akses Terbatas</h2>
        <p style="color: #8899A6; font-size: 14px; margin-bottom: 25px;">
            Halaman ini khusus untuk Pengelola Data BKAD.<br>Silakan masukkan kredensial Admin untuk melanjutkan.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form("form_login", clear_on_submit=False):
            username_input = st.text_input("👤 Username Admin", value="", placeholder="Ketik username...")
            password_input = st.text_input("🔑 Password Admin", type="password", placeholder="Ketik password...")

            st.markdown("")
            submit_login = st.form_submit_button("🔓 Masuk (Login)", use_container_width=True, type="primary")

            if submit_login:
                if login(username_input, password_input):
                    st.success("✅ Login berhasil! Halaman Kelola Data dibuka.")
                    st.rerun()
                else:
                    st.error("❌ Username atau Password salah. Silakan coba lagi.")

        st.caption("💡 *Silakan hubungi Administrator Sistem BKAD untuk mendapatkan akun dan akses.*")
