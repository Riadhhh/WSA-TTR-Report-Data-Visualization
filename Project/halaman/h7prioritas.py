import streamlit as st
import pandas as pd
import plotly.express as px

def show_prioritas(df: pd.DataFrame):
    st.header("🚦 Sebaran Tiket Berdasarkan Prioritas (REPORTED PRIORITY)")

    required_cols = ['REPORTED PRIORITY', 'INCIDENT', 'REPORTED DATE']
    if all(col in df.columns for col in required_cols):
        analysis_df = df.copy()
        analysis_df['REPORTED PRIORITY'] = analysis_df['REPORTED PRIORITY'].fillna('Tidak Diketahui')
        analysis_df['REPORTED DATE'] = pd.to_datetime(analysis_df['REPORTED DATE'], errors='coerce')
        analysis_df['TANGGAL'] = analysis_df['REPORTED DATE'].dt.date

        priority_counts = (
            analysis_df.groupby('REPORTED PRIORITY')['INCIDENT']
            .count()
            .sort_values(ascending=False)
        )

        st.subheader("📋 Tabel Jumlah Tiket per Prioritas")
        st.dataframe(priority_counts)

        priority_df = priority_counts.reset_index()
        priority_df.columns = ['REPORTED PRIORITY', 'JUMLAH TIKET']

        # --- Diagram Batang Vertikal
        st.subheader("📊 Diagram Batang Vertikal")
        fig_bar = px.bar(
            priority_df,
            x='REPORTED PRIORITY',
            y='JUMLAH TIKET',
            color='REPORTED PRIORITY',
            text='JUMLAH TIKET',
            title="Jumlah Tiket Berdasarkan Prioritas"
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(
            xaxis_title="Prioritas",
            yaxis_title="Jumlah Tiket",
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # --- Diagram Batang Horizontal
        st.subheader("📊 Diagram Batang Horizontal")
        fig_bar_h = px.bar(
            priority_df,
            x='JUMLAH TIKET',
            y='REPORTED PRIORITY',
            orientation='h',
            color='REPORTED PRIORITY',
            text='JUMLAH TIKET',
            title="Jumlah Tiket Berdasarkan Prioritas (Horizontal)"
        )
        fig_bar_h.update_traces(textposition='outside')
        fig_bar_h.update_layout(
            xaxis_title="Jumlah Tiket",
            yaxis_title="Prioritas",
            showlegend=False,
            height=500
        )
        st.plotly_chart(fig_bar_h, use_container_width=True)

        # --- Diagram Pie
        st.subheader("🧁 Diagram Pie (Proporsi Tiket per Prioritas)")
        fig_pie = px.pie(
            priority_df,
            names='REPORTED PRIORITY',
            values='JUMLAH TIKET',
            title="Proporsi Tiket per Prioritas",
            hole=0.0
        )
        fig_pie.update_traces(
            pull=[0.1] * len(priority_df),
            textinfo='percent+label'
        )
        fig_pie.update_layout(
            height=500,
            showlegend=True
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.warning("Kolom 'REPORTED PRIORITY', 'INCIDENT', atau 'REPORTED DATE' tidak ditemukan dalam dataset.")
