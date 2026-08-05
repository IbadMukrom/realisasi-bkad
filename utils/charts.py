"""
Modul untuk membuat chart Plotly untuk dashboard realisasi anggaran BKAD.
"""
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import NAMA_BULAN


# Palet warna konsisten
COLORS = {
    "primary": "#2ECC71",      # Hijau utama
    "secondary": "#3498DB",    # Biru
    "accent": "#E74C3C",       # Merah
    "warning": "#F39C12",      # Kuning/oranye
    "info": "#9B59B6",         # Ungu
    "pagu": "#3498DB",         # Biru untuk pagu
    "realisasi": "#2ECC71",    # Hijau untuk realisasi
    "sisa": "#E74C3C",         # Merah untuk sisa
    "bg_dark": "#0E1117",
    "bg_card": "#1B2838",
    "text": "#FAFAFA",
    "text_muted": "#8899A6",
}

COLOR_SEQUENCE = [
    "#2ECC71", "#3498DB", "#E74C3C", "#F39C12", "#9B59B6",
    "#1ABC9C", "#E67E22", "#2980B9", "#C0392B", "#8E44AD",
]

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="Inter, sans-serif"),
    margin=dict(l=20, r=20, t=40, b=20),
    separators=",.",
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(size=11),
    ),
)


def format_rupiah(value: float) -> str:
    """Format angka ke format Rupiah penuh tanpa singkatan (misal: Rp 2.000.000)."""
    try:
        return f"Rp {int(round(value)):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"


def format_rupiah_titik(value: float) -> str:
    """
    Format angka ke Rupiah dengan titik pemisah ribuan (misal: 1.000.000).
    """
    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def parse_rupiah_input(val_str: str) -> float:
    """
    Membersihkan string input (misal '1.000.000', '1,000,000', 'Rp 1.000.000')
    menjadi float angka murni.
    """
    if not val_str:
        return 0.0
    import re
    cleaned = re.sub(r"[^\d]", "", str(val_str))
    return float(cleaned) if cleaned else 0.0


def _merged_layout(**overrides) -> dict:
    """
    Merge LAYOUT_DEFAULTS with overrides, handling nested keys like 'legend'.
    """
    merged = {**LAYOUT_DEFAULTS}
    if "legend" in overrides:
        merged["legend"] = {**LAYOUT_DEFAULTS.get("legend", {}), **overrides.pop("legend")}
    merged.update(overrides)
    return merged


def create_gauge_chart(percentage: float, title: str = "Capaian Realisasi") -> go.Figure:
    """
    Membuat gauge chart persentase capaian realisasi.
    """
    # Warna berdasarkan persentase
    if percentage >= 80:
        bar_color = COLORS["primary"]
    elif percentage >= 50:
        bar_color = COLORS["warning"]
    else:
        bar_color = COLORS["accent"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=percentage,
        number=dict(suffix="%", font=dict(size=42, color=COLORS["text"])),
        title=dict(text=title, font=dict(size=16, color=COLORS["text_muted"])),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickwidth=1,
                tickcolor=COLORS["text_muted"],
                tickfont=dict(color=COLORS["text_muted"]),
            ),
            bar=dict(color=bar_color, thickness=0.75),
            bgcolor="rgba(255,255,255,0.05)",
            borderwidth=0,
            steps=[
                dict(range=[0, 50], color="rgba(231,76,60,0.15)"),
                dict(range=[50, 80], color="rgba(243,156,18,0.15)"),
                dict(range=[80, 100], color="rgba(46,204,113,0.15)"),
            ],
            threshold=dict(
                line=dict(color=COLORS["text"], width=2),
                thickness=0.8,
                value=percentage,
            ),
        ),
    ))

    fig.update_layout(**_merged_layout(height=280))

    return fig


def create_trend_chart(
    monthly_df: pd.DataFrame,
    mode: str = "bulanan",
) -> go.Figure:
    """
    Membuat line/area chart tren realisasi.
    """
    if mode == "bulanan":
        x_col = "nama_bulan"
        y_col = "realisasi_kumulatif"
        title = "📈 Tren Realisasi Kumulatif Bulanan"
        x_order = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
    else:
        x_col = "nama_triwulan"
        y_col = "realisasi_kumulatif"
        title = "📈 Tren Realisasi Kumulatif per Triwulan"
        x_order = [
            "Triwulan I (Jan-Mar)", "Triwulan II (Apr-Jun)",
            "Triwulan III (Jul-Sep)", "Triwulan IV (Okt-Des)",
        ]

    fig = go.Figure()

    # Area fill
    fig.add_trace(go.Scatter(
        x=monthly_df[x_col],
        y=monthly_df[y_col],
        fill="tozeroy",
        fillcolor="rgba(46,204,113,0.15)",
        line=dict(color=COLORS["realisasi"], width=3),
        mode="lines+markers",
        marker=dict(size=8, color=COLORS["realisasi"]),
        name="Realisasi Kumulatif",
        hovertemplate="<b>%{x}</b><br>Realisasi: %{customdata}<extra></extra>",
        customdata=[format_rupiah(v) for v in monthly_df[y_col]],
    ))

    fig.update_layout(
        **_merged_layout(
            title=dict(text=title, font=dict(size=16)),
            xaxis=dict(
                categoryorder="array",
                categoryarray=x_order,
                showgrid=False,
                title="",
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.05)",
                title="",
                tickformat=",.0f",
            ),
            height=400,
            showlegend=False,
        )
    )

    return fig


def create_belanja_comparison(belanja_df: pd.DataFrame) -> go.Figure:
    """
    Membuat grouped bar chart perbandingan pagu vs realisasi per jenis belanja.
    """
    fig = go.Figure()

    # Pagu
    fig.add_trace(go.Bar(
        y=belanja_df["jenis_belanja"],
        x=belanja_df["pagu_anggaran"],
        name="Pagu Anggaran",
        marker_color=COLORS["pagu"],
        orientation="h",
        text=[format_rupiah(v) for v in belanja_df["pagu_anggaran"]],
        textposition="none",
        hovertemplate="<b>%{y}</b><br>Pagu: %{customdata}<extra></extra>",
        customdata=[format_rupiah(v) for v in belanja_df["pagu_anggaran"]],
    ))

    # Realisasi
    fig.add_trace(go.Bar(
        y=belanja_df["jenis_belanja"],
        x=belanja_df["realisasi"],
        name="Realisasi",
        marker_color=COLORS["realisasi"],
        orientation="h",
        text=[f"{p:.1f}%" for p in belanja_df["persentase"]],
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text"]),
        hovertemplate="<b>%{y}</b><br>Realisasi: %{customdata}<extra></extra>",
        customdata=[format_rupiah(v) for v in belanja_df["realisasi"]],
    ))

    fig.update_layout(
        **_merged_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            title=dict(text="📊 Perbandingan Pagu vs Realisasi per Jenis Belanja / Sub-Kegiatan", font=dict(size=16)),
            barmode="group",
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.05)",
                title="",
                tickformat=",.0f",
            ),
            yaxis=dict(
                showgrid=False,
                autorange="reversed",
            ),
            height=max(400, len(belanja_df) * 40 + 100),
        )
    )

    return fig


def create_pj_comparison(pj_df: pd.DataFrame) -> go.Figure:
    """
    Membuat horizontal bar chart perbandingan Pagu vs Realisasi per Bidang Penanggung Jawab.
    """
    fig = go.Figure()

    # Pagu
    fig.add_trace(go.Bar(
        y=pj_df["penanggungjawab"],
        x=pj_df["pagu_anggaran"],
        name="Pagu Anggaran",
        marker_color=COLORS["pagu"],
        orientation="h",
        hovertemplate="<b>%{y}</b><br>Pagu: %{customdata}<extra></extra>",
        customdata=[format_rupiah(v) for v in pj_df["pagu_anggaran"]],
    ))

    # Realisasi
    fig.add_trace(go.Bar(
        y=pj_df["penanggungjawab"],
        x=pj_df["realisasi"],
        name="Realisasi",
        marker_color=COLORS["realisasi"],
        orientation="h",
        text=[f"{p:.1f}%" for p in pj_df["persentase"]],
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text"]),
        hovertemplate="<b>%{y}</b><br>Realisasi: %{customdata}<extra></extra>",
        customdata=[format_rupiah(v) for v in pj_df["realisasi"]],
    ))

    fig.update_layout(
        **_merged_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            title=dict(text="🏢 Capaian Realisasi per Bidang Penanggung Jawab", font=dict(size=16)),
            barmode="group",
            height=max(320, len(pj_df) * 50 + 100),
            yaxis=dict(autorange="reversed"),
        )
    )

    return fig


def create_donut_chart(composition_df: pd.DataFrame) -> go.Figure:
    """
    Membuat donut chart komposisi realisasi per jenis belanja.
    """
    fig = go.Figure(go.Pie(
        labels=composition_df["jenis_belanja"],
        values=composition_df["realisasi"],
        hole=0.55,
        marker=dict(colors=COLOR_SEQUENCE[:len(composition_df)]),
        textinfo="percent+label",
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text"]),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Realisasi: %{customdata}<br>"
            "Proporsi: %{percent}<extra></extra>"
        ),
        customdata=[format_rupiah(v) for v in composition_df["realisasi"]],
    ))

    fig.update_layout(
        **_merged_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=10),
            ),
            title=dict(text="🥧 Komposisi Realisasi per Jenis Belanja", font=dict(size=16)),
            height=420,
            showlegend=True,
            annotations=[
                dict(
                    text="Realisasi",
                    x=0.5, y=0.5,
                    font=dict(size=14, color=COLORS["text_muted"]),
                    showarrow=False,
                )
            ],
        )
    )

    return fig


def create_heatmap_belanja_monthly(df: pd.DataFrame) -> go.Figure:
    """
    Membuat heatmap persentase realisasi per jenis belanja per bulan.
    """
    agg = (
        df.groupby(["jenis_belanja", "bulan"])
        .agg(
            pagu_anggaran=("pagu_anggaran", "sum"),
            realisasi=("realisasi", "sum"),
        )
        .reset_index()
    )
    agg["persentase"] = (agg["realisasi"] / agg["pagu_anggaran"] * 100).round(1)

    pivot = agg.pivot(index="jenis_belanja", columns="bulan", values="persentase").fillna(0)

    # Rename columns to bulan names
    pivot.columns = [NAMA_BULAN[b] for b in pivot.columns]

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[
            [0, "rgba(231,76,60,0.3)"],
            [0.5, "rgba(243,156,18,0.5)"],
            [0.8, "rgba(46,204,113,0.5)"],
            [1, "rgba(46,204,113,0.9)"],
        ],
        text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(size=10, color=COLORS["text"]),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>",
        colorbar=dict(
            title=dict(
                text="Realisasi %",
                font=dict(color=COLORS["text_muted"]),
            ),
            tickfont=dict(color=COLORS["text_muted"]),
        ),
    ))

    fig.update_layout(
        **_merged_layout(
            title=dict(text="🗓️ Heatmap Realisasi per Jenis Belanja per Bulan", font=dict(size=16)),
            xaxis=dict(title="", side="bottom"),
            yaxis=dict(title="", autorange="reversed"),
            height=max(300, len(pivot) * 45),
        )
    )

    return fig
