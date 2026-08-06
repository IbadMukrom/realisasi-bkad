"""
Modul untuk membuat chart Plotly untuk dashboard realisasi anggaran BKAD.
"""
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import NAMA_BULAN


# Palet warna konsisten & premium
COLORS = {
    "primary": "#00E676",      # Emerald Green Glow
    "secondary": "#29B6F6",    # Electric Blue
    "accent": "#FF5252",       # Coral Red
    "warning": "#FFCA28",      # Amber Gold
    "info": "#AB47BC",         # Vivid Purple
    "pagu": "#29B6F6",         # Electric Blue untuk pagu
    "realisasi": "#00E676",    # Emerald Green untuk realisasi
    "sisa": "#FF5252",         # Coral Red untuk sisa
    "bg_dark": "#0E1117",
    "bg_card": "#1B2838",
    "text": "#F8FAFC",
    "text_muted": "#94A3B8",
}

COLOR_SEQUENCE = [
    "#00E676", "#29B6F6", "#FF5252", "#FFCA28", "#AB47BC",
    "#26A69A", "#FFA726", "#42A5F5", "#EC407A", "#7E57C2",
]

LAYOUT_DEFAULTS = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="Inter, sans-serif"),
    margin=dict(l=20, r=30, t=20, b=20),
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
    if percentage >= 80:
        bar_color = COLORS["primary"]
    elif percentage >= 50:
        bar_color = COLORS["warning"]
    else:
        bar_color = COLORS["accent"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        number=dict(suffix="%", font=dict(size=42, color=COLORS["text"])),
        title=dict(text="", font=dict(size=1)),
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
        x_order = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
    else:
        x_col = "nama_triwulan"
        y_col = "realisasi_kumulatif"
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
            title="",
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
            margin=dict(l=20, r=20, t=20, b=20),
            height=360,
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
            title="",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            barmode="group",
            margin=dict(l=20, r=50, t=30, b=20),
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
            height=max(360, len(belanja_df) * 45 + 80),
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
            title="",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            barmode="group",
            margin=dict(l=20, r=50, t=30, b=20),
            height=max(300, len(pj_df) * 50 + 80),
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
            title="",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.5,
                font=dict(size=10),
            ),
            margin=dict(l=20, r=20, t=20, b=60),
            height=380,
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
            title="",
            xaxis=dict(title="", side="bottom"),
            yaxis=dict(title="", autorange="reversed"),
            margin=dict(l=20, r=20, t=20, b=20),
            height=max(280, len(pivot) * 45),
        )
    )

    return fig
