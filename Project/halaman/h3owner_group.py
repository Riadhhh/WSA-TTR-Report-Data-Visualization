import streamlit as st
import pandas as pd
import plotly.express as px

def show_owner_group(df: pd.DataFrame):
    st.header("🏢 Analisis Owner Group dengan Tiket Terbanyak")

    if 'OWNER GROUP' in df.columns and 'INCIDENT' in df.columns:
        filtered_df = df[df['OWNER GROUP'] != 'Tidak Diketahui']

        owner_group_counts = (
            filtered_df.groupby('OWNER GROUP')['INCIDENT']
            .count()
            .sort_values(ascending=False)
        )

        st.subheader("📋 Tabel Jumlah Tiket per Owner Group")
        st.dataframe(owner_group_counts)

        unique_owner_groups = filtered_df['OWNER GROUP'].nunique()
        min_slider = min(5, unique_owner_groups)
        top_n = st.slider(
            "Pilih jumlah Top 'Owner Group' yang ingin ditampilkan:",
            min_value=min_slider,
            max_value=unique_owner_groups,
            value=min(10, unique_owner_groups)
        )

        top_owner_group_counts = owner_group_counts.nlargest(top_n)

        owner_group_df = top_owner_group_counts.reset_index()
        owner_group_df.columns = ['OWNER GROUP', 'JUMLAH TIKET']

        # --- Diagram Batang Vertikal
        st.subheader("📊 Diagram Batang Vertikal")
        st.write(f"Visualisasi ini mengurutkan {top_n} Owner Group yang paling banyak menangani tiket.")
        fig_bar = px.bar(
            owner_group_df,
            x='OWNER GROUP',
            y='JUMLAH TIKET',
            color='OWNER GROUP',
            text='JUMLAH TIKET',
            title=f"Top {top_n} Owner Group dengan Tiket Terbanyak"
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(
            xaxis_title="Owner Group",
            yaxis_title="Jumlah Tiket",
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # --- Diagram Batang Horizontal
        st.subheader("📊 Diagram Batang Horizontal")
        fig_bar_h = px.bar(
            owner_group_df,
            x='JUMLAH TIKET',
            y='OWNER GROUP',
            orientation='h',
            color='OWNER GROUP',
            text='JUMLAH TIKET',
            title=f"Top {top_n} Owner Group dengan Tiket Terbanyak (Horizontal)"
        )
        fig_bar_h.update_traces(textposition='outside')
        fig_bar_h.update_layout(
            xaxis_title="Jumlah Tiket",
            yaxis_title="Owner Group",
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig_bar_h, use_container_width=True)

        # --- Dot Plot
        st.subheader("🔵 Dot Plot (Perbandingan Owner Group)")
        fig_dot = px.scatter(
            owner_group_df,
            x='JUMLAH TIKET',
            y='OWNER GROUP',
            color='JUMLAH TIKET',
            size='JUMLAH TIKET',
            text='JUMLAH TIKET',
            color_continuous_scale='blugrn',
            title=f"Dot Plot Jumlah Tiket per Owner Group (Top {top_n})"
        )
        fig_dot.update_traces(textposition='top right')
        fig_dot.update_layout(
            xaxis_title="Jumlah Tiket",
            yaxis_title="Owner Group",
            height=600,
            showlegend=False
        )
        st.plotly_chart(fig_dot, use_container_width=True)

    else:
        st.warning("Kolom 'OWNER GROUP' atau 'INCIDENT' tidak ditemukan dalam dataset.")
