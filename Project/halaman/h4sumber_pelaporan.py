import streamlit as st
import pandas as pd

def show_sumber_pelaporan(df: pd.DataFrame):
    st.header("📥 Analisis Sumber Pelaporan Tiket Paling Umum")

    if 'SOURCE TICKET' in df.columns and 'INCIDENT' in df.columns:
        filtered_df = df[df['SOURCE TICKET'] != 'Tidak Diketahui']
        source_ticket_counts = (
            filtered_df.groupby('SOURCE TICKET')['INCIDENT']
            .count()
            .sort_values(ascending=False)
        )

        st.subheader("📋 Tabel Jumlah Tiket per Sumber Pelaporan")
        st.dataframe(source_ticket_counts)

        if source_ticket_counts.nunique() <= 1:
            st.info("⚠️ Hanya ada satu kategori yang valid, visualisasi tidak ditampilkan.")
        else:
            st.warning("📌 Kategori sudah lebih dari satu, tapi visualisasi belum dibuat. Tambahkan jika diperlukan.")
    else:
        st.warning("Kolom 'SOURCE TICKET' atau 'INCIDENT' tidak ditemukan dalam dataset.")
