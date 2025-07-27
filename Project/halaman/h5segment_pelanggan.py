import streamlit as st
import pandas as pd

def show_segment_pelanggan(df: pd.DataFrame):
    st.header("👥 Analisis Proporsi Tiket Berdasarkan Segmen Pelanggan")

    if 'CUSTOMER SEGMENT' in df.columns and 'INCIDENT' in df.columns:
        filtered_df = df[df['CUSTOMER SEGMENT'] != 'Tidak Diketahui']
        segment_counts = (
            filtered_df.groupby('CUSTOMER SEGMENT')['INCIDENT']
            .count()
            .sort_values(ascending=False)
        )

        st.subheader("📋 Tabel Jumlah Tiket per Segmen Pelanggan")
        st.dataframe(segment_counts)

        if segment_counts.nunique() <= 1:
            st.info("⚠️ Hanya ada satu kategori yang valid, visualisasi tidak ditampilkan.")
        else:
            st.warning("📌 Kategori sudah lebih dari satu, tapi visualisasi belum dibuat. Tambahkan jika diperlukan.")
    else:
        st.warning("Kolom 'CUSTOMER SEGMENT' atau 'INCIDENT' tidak ditemukan dalam dataset.")
