import streamlit as st
import pandas as pd
import plotly.express as px

def show_status(df: pd.DataFrame):
    st.header("📊 Analisis Distribusi Tiket Berdasarkan Status")

    if 'STATUS' in df.columns and 'INCIDENT' in df.columns:
        # Hapus baris dengan status 'Tidak Diketahui'
        filtered_df = df[df['STATUS'] != 'Tidak Diketahui']

        # Hitung jumlah insiden per status
        status_counts = filtered_df.groupby('STATUS')['INCIDENT'].count().sort_values(ascending=False)

        st.subheader("📋 Tabel Jumlah Tiket per Status")
        st.dataframe(status_counts)

        # Slider untuk memilih Top N Status
        unique_status = filtered_df['STATUS'].nunique()
        min_slider = min(3, unique_status)
        top_n = st.slider(
            "Pilih jumlah Top 'Status' yang ingin ditampilkan:",
            min_value=min_slider,
            max_value=unique_status,
            value=min(4, unique_status)
        )

        # Ambil Top N status
        top_status_counts = status_counts.nlargest(top_n)

        # Ubah jadi dataframe untuk plot
        status_df = top_status_counts.reset_index()
        status_df.columns = ['STATUS', 'JUMLAH TIKET']

        # --- Diagram Batang Vertikal
        st.subheader("📶 Diagram Batang Vertikal")
        st.write(f"Visualisasi ini mengurutkan {top_n} Status dengan jumlah tiket terbanyak.")
        fig_bar = px.bar(
            status_df,
            x='STATUS',
            y='JUMLAH TIKET',
            color='STATUS',
            text='JUMLAH TIKET',
            title=f"Top {top_n} Status dengan Jumlah Tiket Terbanyak"
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(
            xaxis_title="Status",
            yaxis_title="Jumlah Tiket",
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # --- Diagram Batang Horizontal
        st.subheader("📶 Diagram Batang Horizontal")
        fig_bar_h = px.bar(
            status_df,
            x='JUMLAH TIKET',
            y='STATUS',
            orientation='h',
            color='STATUS',
            text='JUMLAH TIKET',
            title=f"Top {top_n} Status dengan Jumlah Tiket Terbanyak (Horizontal)"
        )
        fig_bar_h.update_traces(textposition='outside')
        fig_bar_h.update_layout(
            xaxis_title="Jumlah Tiket",
            yaxis_title="Status",
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig_bar_h, use_container_width=True)

        # --- Diagram Pie
        st.subheader("🧁 Diagram Pie (Proporsi Tiket per Status)")
        fig_pie = px.pie(
            status_df,
            names='STATUS',
            values='JUMLAH TIKET',
            title=f"Proporsi Top {top_n} Status Tiket",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=500)
        st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.warning("Kolom 'STATUS' atau 'INCIDENT' tidak ditemukan dalam dataset.")
