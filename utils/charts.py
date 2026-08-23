"""
Modul untuk membuat chart Plotly untuk dashboard realisasi anggaran BKAD.
"""
import textwrap
from typing import Any, Optional
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


def parse_rupiah_input(val_str: Any) -> float:
    """
    Membersihkan string input (misal '1.000.000', '1,000,000', 'Rp 1.000.000')
    menjadi float angka murni secara aman.
    """
    if val_str is None or pd.isna(val_str):
        return 0.0
    if isinstance(val_str, (int, float)):
        return float(val_str)

    val = str(val_str).strip()
    if not val:
        return 0.0

    import re
    if re.match(r"^\d+\.\d+$", val) and val.count(".") == 1 and "," not in val:
        try:
            return float(val)
        except ValueError:
            pass

    cleaned = re.sub(r"[^\d]", "", val)
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


def format_rupiah_ringkas(value: float) -> str:
    """Format angka ke format Rupiah ringkas (misal: Rp 40 Miliar, Rp 1,5 Triliun)."""
    try:
        val = float(value)
        abs_val = abs(val)
        if abs_val >= 1e12:
            return f"≈ Rp {val / 1e12:.2f} Triliun".replace(".", ",")
        elif abs_val >= 1e9:
            return f"≈ Rp {val / 1e9:.2f} Miliar".replace(".", ",")
        elif abs_val >= 1e6:
            return f"≈ Rp {val / 1e6:.2f} Juta".replace(".", ",")
        elif abs_val >= 1e3:
            return f"≈ Rp {val / 1e3:.1f} Ribu".replace(".", ",")
        else:
            return f"Rp {int(val):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"


def format_rupiah_sumbu(value: float) -> str:
    """Format angka untuk label sumbu chart (misal: 40 M, 300 Jt)."""
    try:
        val = float(value)
        abs_val = abs(val)
        if abs_val >= 1e12:
            return f"{val / 1e12:.1f} T".replace(".0 T", " T").replace(".", ",")
        elif abs_val >= 1e9:
            return f"{val / 1e9:.1f} M".replace(".0 M", " M").replace(".", ",")
        elif abs_val >= 1e6:
            return f"{val / 1e6:.1f} Jt".replace(".0 Jt", " Jt").replace(".", ",")
        elif abs_val >= 1e3:
            return f"{val / 1e3:.0f} Rb"
        else:
            return f"{int(val):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def create_gauge_chart(percentage: float, title: str = "Capaian Realisasi") -> go.Figure:
    """
    Membuat gauge chart persentase capaian realisasi yang modern & elegan.
    """
    pct = max(0.0, min(100.0, float(percentage)))

    if pct >= 80:
        bar_color = "#00E676"  # Emerald Green Glow
        status_text = "Target Sangat Baik"
        status_color = "#00E676"
    elif pct >= 50:
        bar_color = "#FFCA28"  # Amber Gold
        status_text = "Cukup / On-Track"
        status_color = "#FFCA28"
    else:
        bar_color = "#FF5252"  # Coral Red
        status_text = "Perlu Perhatian"
        status_color = "#FF5252"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number=dict(
            suffix="%",
            font=dict(size=36, color="#FFFFFF", family="Inter, sans-serif"),
        ),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickwidth=1,
                tickcolor=COLORS["text_muted"],
                tickfont=dict(color=COLORS["text_muted"], size=10),
                tickvals=[0, 25, 50, 75, 100],
                ticksuffix="%",
            ),
            bar=dict(
                color=bar_color,
                thickness=0.76,
                line=dict(color="rgba(255,255,255,0.25)", width=1)
            ),
            bgcolor="rgba(255,255,255,0.06)",
            borderwidth=0,
            steps=[
                dict(range=[0, 50], color="rgba(255, 82, 82, 0.08)"),
                dict(range=[50, 80], color="rgba(255, 202, 40, 0.08)"),
                dict(range=[80, 100], color="rgba(0, 230, 118, 0.08)"),
            ],
            threshold=dict(
                line=dict(color="#FFFFFF", width=3),
                thickness=0.82,
                value=pct,
            ),
        ),
    ))

    fig.update_layout(
        **_merged_layout(
            margin=dict(l=25, r=25, t=25, b=20),
            height=285,
            annotations=[
                dict(
                    text=f"<span style='color:{status_color};font-weight:700;font-size:12px;'>● {status_text}</span>",
                    x=0.5,
                    y=0.12,
                    showarrow=False,
                )
            ]
        )
    )

    return fig


def create_trend_chart(
    monthly_df: pd.DataFrame,
    mode: str = "bulanan",
) -> go.Figure:
    """
    Membuat area chart tren realisasi yang modern, mewah, dan responsif.
    """
    if monthly_df.empty:
        fig = go.Figure()
        fig.update_layout(
            **_merged_layout(
                annotations=[dict(text="Tidak ada data tren", showarrow=False, font=dict(size=14, color=COLORS["text_muted"]))],
                height=340
            )
        )
        return fig

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

    # Glowing Area Fill + Smooth Spline Line
    fig.add_trace(go.Scatter(
        x=monthly_df[x_col],
        y=monthly_df[y_col],
        fill="tozeroy",
        fillcolor="rgba(0, 230, 118, 0.14)",
        line=dict(color="#00E676", width=3.5, shape="spline", smoothing=1.3),
        mode="lines+markers",
        marker=dict(
            size=9,
            color="#00E676",
            line=dict(color="#FFFFFF", width=2),
            symbol="circle"
        ),
        name="Realisasi Kumulatif",
        customdata=[format_rupiah(v) for v in monthly_df[y_col]],
        hovertemplate="📅 <b>%{x}</b><br>💰 Realisasi: <b>%{customdata}</b><extra></extra>",
    ))

    fig.update_layout(
        **_merged_layout(
            title="",
            xaxis=dict(
                categoryorder="array",
                categoryarray=x_order,
                showgrid=False,
                title="",
                tickfont=dict(size=11, color=COLORS["text"]),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.06)",
                title="",
                tickfont=dict(size=10.5, color=COLORS["text_muted"]),
            ),
            margin=dict(l=25, r=25, t=25, b=25),
            height=340,
            showlegend=False,
        )
    )

    return fig


def create_belanja_comparison(belanja_df: pd.DataFrame, max_items: Optional[int] = None) -> go.Figure:
    """
    Membuat grouped bar chart perbandingan pagu vs realisasi per jenis belanja.
    """
    if belanja_df.empty:
        fig = go.Figure()
        fig.update_layout(
            **_merged_layout(
                annotations=[dict(text="Tidak ada data belanja", showarrow=False, font=dict(size=14, color=COLORS["text_muted"]))],
                height=300,
            )
        )
        return fig

    df_plot = belanja_df.copy()
    if max_items and len(df_plot) > max_items:
        df_plot = df_plot.iloc[:max_items]

    # Wrap long labels untuk Y-axis
    wrapped_labels = [_wrap_label(lbl, width=32) for lbl in df_plot["jenis_belanja"]]
    original_labels = df_plot["jenis_belanja"].tolist()

    fig = go.Figure()

    # Pagu
    pagu_hover = [
        f"<b>{name}</b><br>Pagu Anggaran: <b>{format_rupiah(v)}</b>"
        for name, v in zip(original_labels, df_plot["pagu_anggaran"])
    ]
    fig.add_trace(go.Bar(
        y=wrapped_labels,
        x=df_plot["pagu_anggaran"],
        name="Pagu Anggaran",
        marker_color=COLORS["pagu"],
        marker_line=dict(width=0),
        orientation="h",
        hovertext=pagu_hover,
        hovertemplate="%{hovertext}<extra></extra>",
    ))

    # Realisasi
    real_hover = [
        f"<b>{name}</b><br>Realisasi: <b>{format_rupiah(v)}</b> ({p:.1f}%)"
        for name, v, p in zip(original_labels, df_plot["realisasi"], df_plot["persentase"])
    ]
    fig.add_trace(go.Bar(
        y=wrapped_labels,
        x=df_plot["realisasi"],
        name="Realisasi",
        marker_color=COLORS["realisasi"],
        marker_line=dict(width=0),
        orientation="h",
        text=[f" {p:.1f}%" for p in df_plot["persentase"]],
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text"]),
        cliponaxis=False,
        hovertext=real_hover,
        hovertemplate="%{hovertext}<extra></extra>",
    ))

    row_height = 46
    total_height = max(340, len(df_plot) * row_height + 90)

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
            bargap=0.25,
            bargroupgap=0.1,
            margin=dict(l=220, r=50, t=35, b=25),
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.06)",
                title="",
                tickformat=",.0f",
                tickfont=dict(size=10, color=COLORS["text_muted"]),
            ),
            yaxis=dict(
                showgrid=False,
                autorange="reversed",
                tickfont=dict(size=10.5, color=COLORS["text"]),
            ),
            height=total_height,
        )
    )

    return fig


def create_pj_comparison(pj_df: pd.DataFrame) -> go.Figure:
    """
    Membuat horizontal bar chart perbandingan Pagu vs Realisasi per Bidang Penanggung Jawab.
    """
    if pj_df.empty:
        fig = go.Figure()
        return fig

    wrapped_labels = [_wrap_label(lbl, width=30) for lbl in pj_df["penanggungjawab"]]
    original_labels = pj_df["penanggungjawab"].tolist()

    fig = go.Figure()

    # Pagu
    pagu_hover = [
        f"<b>{name}</b><br>Pagu Anggaran: <b>{format_rupiah(v)}</b>"
        for name, v in zip(original_labels, pj_df["pagu_anggaran"])
    ]
    fig.add_trace(go.Bar(
        y=wrapped_labels,
        x=pj_df["pagu_anggaran"],
        name="Pagu Anggaran",
        marker_color=COLORS["pagu"],
        orientation="h",
        hovertext=pagu_hover,
        hovertemplate="%{hovertext}<extra></extra>",
    ))

    # Realisasi
    real_hover = [
        f"<b>{name}</b><br>Realisasi: <b>{format_rupiah(v)}</b> ({p:.1f}%)"
        for name, v, p in zip(original_labels, pj_df["realisasi"], pj_df["persentase"])
    ]
    fig.add_trace(go.Bar(
        y=wrapped_labels,
        x=pj_df["realisasi"],
        name="Realisasi",
        marker_color=COLORS["realisasi"],
        orientation="h",
        text=[f" {p:.1f}%" for p in pj_df["persentase"]],
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text"]),
        cliponaxis=False,
        hovertext=real_hover,
        hovertemplate="%{hovertext}<extra></extra>",
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
            bargap=0.25,
            bargroupgap=0.1,
            margin=dict(l=190, r=50, t=35, b=20),
            height=max(300, len(pj_df) * 48 + 80),
            yaxis=dict(autorange="reversed", tickfont=dict(size=11, color=COLORS["text"])),
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(255,255,255,0.06)",
                title="",
                tickformat=",.0f",
                tickfont=dict(size=10, color=COLORS["text_muted"]),
            ),
        )
    )

    return fig


def create_donut_chart(composition_df: pd.DataFrame, max_slices: int = 5) -> go.Figure:
    """
    Membuat donut chart komposisi realisasi per jenis belanja yang rapi dan elegan.
    Otomatis menggabungkan slice kecil ke 'Lainnya' agar tidak tumpang tindih.
    """
    if composition_df.empty or composition_df["realisasi"].sum() == 0:
        fig = go.Figure()
        fig.update_layout(
            **_merged_layout(
                annotations=[dict(text="Tidak ada data realisasi", showarrow=False, font=dict(size=14, color=COLORS["text_muted"]))],
                height=380,
            )
        )
        return fig

    df_comp = composition_df.copy().sort_values("realisasi", ascending=False)
    total_realisasi = df_comp["realisasi"].sum()

    # Smart grouping untuk mencegah label bertabrakan jika slice terlalu banyak
    if len(df_comp) > max_slices:
        top_df = df_comp.iloc[:max_slices].copy()
        other_realisasi = df_comp.iloc[max_slices:]["realisasi"].sum()
        other_count = len(df_comp) - max_slices
        other_row = pd.DataFrame([{
            "jenis_belanja": f"Lainnya ({other_count} Sub-Kegiatan)",
            "realisasi": other_realisasi,
            "persentase_komposisi": round(other_realisasi / total_realisasi * 100, 2)
        }])
        plot_df = pd.concat([top_df, other_row], ignore_index=True)
    else:
        plot_df = df_comp

    # Format ringkas total realisasi untuk center text
    if total_realisasi >= 1e12:
        total_str = f"Rp {total_realisasi / 1e12:.2f} T"
    elif total_realisasi >= 1e9:
        total_str = f"Rp {total_realisasi / 1e9:.2f} M"
    elif total_realisasi >= 1e6:
        total_str = f"Rp {total_realisasi / 1e6:.2f} Jt"
    else:
        total_str = format_rupiah(total_realisasi)

    # Truncate label untuk legend
    clean_labels = []
    for lbl in plot_df["jenis_belanja"]:
        if len(lbl) > 28:
            clean_labels.append(lbl[:26] + "...")
        else:
            clean_labels.append(lbl)

    palette = [
        "#00E676", "#29B6F6", "#FFCA28", "#AB47BC", "#FF5252",
        "#26A69A", "#FFA726", "#42A5F5", "#EC407A", "#64748B"
    ]
    colors = palette[:len(plot_df)]
    if "Lainnya" in plot_df.iloc[-1]["jenis_belanja"]:
        colors[-1] = "#64748B"

    donut_hover = [
        f"<b>{name}</b><br>💰 Realisasi: <b>{format_rupiah(v)}</b>"
        for name, v in zip(plot_df["jenis_belanja"], plot_df["realisasi"])
    ]

    fig = go.Figure(go.Pie(
        labels=clean_labels,
        values=plot_df["realisasi"],
        hole=0.62,
        marker=dict(
            colors=colors,
            line=dict(color="#0E1117", width=2)
        ),
        textinfo="percent",
        textposition="inside",
        textfont=dict(size=11, color="#FFFFFF", family="Inter, sans-serif"),
        insidetextorientation="horizontal",
        hovertext=donut_hover,
        hovertemplate="%{hovertext}<br>📊 Porsi: <b>%{percent}</b><extra></extra>",
    ))

    fig.update_layout(
        **_merged_layout(
            title="",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.08,
                xanchor="center",
                x=0.5,
                font=dict(size=10, color=COLORS["text_muted"]),
            ),
            margin=dict(l=10, r=10, t=20, b=80),
            height=430,
            showlegend=True,
            annotations=[
                dict(
                    text=f"<b style='color:#F8FAFC;font-size:15px;'>{total_str}</b><br><span style='color:#94A3B8;font-size:11px;'>Total Realisasi</span>",
                    x=0.5, y=0.5,
                    showarrow=False,
                )
            ],
        )
    )

    return fig


def _wrap_label(text: str, width: int = 36) -> str:
    """Bungkus teks label yang panjang dengan <br> agar rapi di sumbu Y."""
    if not text or pd.isna(text):
        return ""
    text_str = str(text).strip()
    if len(text_str) <= width:
        return text_str
    lines = textwrap.wrap(text_str, width=width, break_long_words=False)
    return "<br>".join(lines)


def create_heatmap_belanja_monthly(
    df: pd.DataFrame,
    group_col: str = "jenis_belanja",
    max_items: Optional[int] = None
) -> go.Figure:
    """
    Membuat heatmap persentase realisasi per jenis belanja / bidang per bulan dengan desain modern & rapi.
    """
    if df.empty or group_col not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            **_merged_layout(
                annotations=[
                    dict(
                        text="Tidak ada data untuk ditampilkan pada Heatmap",
                        showarrow=False,
                        font=dict(size=14, color=COLORS["text_muted"]),
                    )
                ],
                height=250,
            )
        )
        return fig

    agg = (
        df.groupby([group_col, "bulan"])
        .agg(
            pagu_anggaran=("pagu_anggaran", "sum"),
            realisasi=("realisasi", "sum"),
        )
        .reset_index()
    )
    agg["persentase"] = (
        agg["realisasi"] / agg["pagu_anggaran"].replace(0, float("nan")) * 100
    ).fillna(0).round(1)

    pivot = agg.pivot(index=group_col, columns="bulan", values="persentase").fillna(0)

    if pivot.empty:
        fig = go.Figure()
        fig.update_layout(
            **_merged_layout(
                annotations=[
                    dict(
                        text="Data tidak mencukupi untuk membuat heatmap",
                        showarrow=False,
                        font=dict(size=14, color=COLORS["text_muted"]),
                    )
                ],
                height=250,
            )
        )
        return fig

    # Urutkan berdasarkan rata-rata realisasi tertinggi agar rapi & hierarkis
    avg_realisasi = pivot.mean(axis=1)
    pivot = pivot.loc[avg_realisasi.sort_values(ascending=False).index]

    if max_items and len(pivot) > max_items:
        pivot = pivot.iloc[:max_items]

    # Map nama bulan secara terurut
    ordered_months = [b for b in sorted(pivot.columns) if b in NAMA_BULAN]
    if ordered_months:
        pivot = pivot[ordered_months]
        pivot.columns = [NAMA_BULAN[b] for b in ordered_months]

    original_labels = [str(idx) for idx in pivot.index.tolist()]
    wrapped_labels = [_wrap_label(lbl, width=38) for lbl in original_labels]

    # Format teks di dalam sel
    text_matrix = []
    for row in pivot.values:
        row_text = []
        for v in row:
            if v == 0:
                row_text.append("0%")
            elif v >= 100:
                row_text.append(f"{v:.0f}%")
            else:
                row_text.append(f"{v:.1f}%")
        text_matrix.append(row_text)

    # Palet warna modern dark theme dengan transisi halus
    colorscale = [
        [0.0, "#131b2e"],       # Dark slate blue untuk 0%
        [0.05, "#1f293d"],      # Slate
        [0.2, "#881337"],       # Merah marun untuk realisasi rendah (<20%)
        [0.45, "#b45309"],      # Amber untuk realisasi sedang (20-50%)
        [0.7, "#047857"],       # Emerald green untuk realisasi baik (50-80%)
        [0.9, "#10b981"],       # Terang emerald (80-99%)
        [1.0, "#00E676"],       # Neon emerald untuk capaian 100%+
    ]

    # Hovertext untuk detail lengkap (nama tanpa dipotong <br>)
    heatmap_hover = []
    for orig_name, row_vals in zip(original_labels, pivot.values):
        row_hover = [
            f"<b>{orig_name}</b><br>📅 Bulan: <b>{col_name}</b><br>📊 Realisasi: <b>{val:.1f}%</b>"
            for col_name, val in zip(pivot.columns, row_vals)
        ]
        heatmap_hover.append(row_hover)

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=wrapped_labels,
            hovertext=heatmap_hover,
            colorscale=colorscale,
            zmin=0,
            zmax=100,
            xgap=4,
            ygap=4,
            text=text_matrix,
            texttemplate="%{text}",
            textfont=dict(size=11, color="#FFFFFF", family="Inter, sans-serif"),
            hovertemplate="%{hovertext}<extra></extra>",
            colorbar=dict(
                title=dict(
                    text="<b>Realisasi</b>",
                    font=dict(color=COLORS["text"], size=12),
                    side="top",
                ),
                tickfont=dict(color=COLORS["text_muted"], size=10),
                ticksuffix="%",
                tickvals=[0, 25, 50, 75, 100],
                thickness=14,
                len=0.8,
                outlinewidth=0,
            ),
        )
    )

    # Dynamic margin and height calculation
    left_margin = 250 if group_col == "jenis_belanja" else 180
    row_height = 42
    total_height = max(300, len(pivot) * row_height + 100)

    fig.update_layout(
        **_merged_layout(
            title="",
            xaxis=dict(
                title="",
                side="top",
                tickfont=dict(size=11, color=COLORS["text"]),
                gridcolor="rgba(0,0,0,0)",
                showgrid=False,
            ),
            yaxis=dict(
                title="",
                autorange="reversed",
                tickfont=dict(size=10.5, color=COLORS["text"]),
                gridcolor="rgba(0,0,0,0)",
                showgrid=False,
            ),
            margin=dict(l=left_margin, r=20, t=60, b=30),
            height=total_height,
        )
    )

    return fig
