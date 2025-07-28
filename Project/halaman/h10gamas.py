import streamlit as st
import pandas as pd
import plotly.express as px

def show_is_not_gamas(df: pd.DataFrame):
    st.header("⏱️ Analisis Keterkaitan 'IS NOT GAMAS' dan Durasi Penyelesaian")

    # --- Validasi Kolom ---
    durasi_col = "SISA DURASI TTR OPEN"
    status_col = "IS NOT GAMAS"

    if durasi_col not in df.columns or status_col not in df.columns:
        st.error(f"Kolom '{durasi_col}' atau '{status_col}' tidak ditemukan dalam dataset.")
        return

    # --- Filter Data ---
    filtered_df = df[[status_col, durasi_col]].copy()
    filtered_df.dropna(inplace=True)

    # Pastikan tipe data durasi numerik
    filtered_df[durasi_col] = pd.to_numeric(filtered_df[durasi_col], errors='coerce')
    filtered_df.dropna(inplace=True)

    # Label boolean sebagai teks (untuk kejelasan di boxplot)
    filtered_df["Kategori GAMAS"] = filtered_df[status_col].map({True: "Non-GAMAS", False: "GAMAS"})

    # --- Statistik Deskriptif ---
    st.subheader("📊 Rata-rata dan Median Durasi Penyelesaian")
    summary_stats = filtered_df.groupby("Kategori GAMAS")[durasi_col].agg(["count", "mean", "median"]).round(2)
    summary_stats.rename(columns={"count": "Jumlah Tiket", "mean": "Rata-rata Durasi", "median": "Median Durasi"}, inplace=True)
    st.dataframe(summary_stats)

    # --- Boxplot ---
    st.subheader("🧪 Boxplot Perbandingan Durasi Penyelesaian")
    fig = px.box(
        filtered_df,
        x="Kategori GAMAS",
        y=durasi_col,
        color="Kategori GAMAS",
        title="Perbandingan Durasi Penyelesaian antara GAMAS dan Non-GAMAS",
        points="all"
    )
    fig.update_layout(
        xaxis_title="Kategori Insiden",
        yaxis_title="Durasi Penyelesaian (SISA DURASI TTR OPEN)",
        showlegend=False,
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Interpretasi Awal ---
    st.subheader("📝 Interpretasi Sementara")
    st.info("""
    - Jika boxplot untuk **Non-GAMAS** (True) terlihat **lebih tinggi** dibanding GAMAS, artinya kemungkinan besar insiden Non-GAMAS diselesaikan lebih lama.
    - Outlier (titik ekstrem) bisa menunjukkan insiden yang jauh lebih lama dari biasanya.
    """)

    # --- Penutup (opsional dinamis) ---
    if summary_stats.loc["Non-GAMAS", "Rata-rata Durasi"] > summary_stats.loc["GAMAS", "Rata-rata Durasi"]:
        st.success("📌 Rata-rata durasi penyelesaian insiden Non-GAMAS lebih tinggi dari GAMAS.")
    elif summary_stats.loc["Non-GAMAS", "Rata-rata Durasi"] < summary_stats.loc["GAMAS", "Rata-rata Durasi"]:
        st.success("📌 Insiden GAMAS membutuhkan waktu penyelesaian lebih tinggi dari Non-GAMAS.")
    else:
        st.info("📌 Tidak ada perbedaan signifikan dalam rata-rata durasi penyelesaian antara GAMAS dan Non-GAMAS.")
