import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def show_korelasi_ttr(df: pd.DataFrame):
    st.header("📈 Analisis Korelasi: Kepatuhan TTR")

    # Bersihkan kolom dari spasi
    df.columns = df.columns.str.strip()

    # Validasi kolom utama
    if 'INCIDENT' not in df.columns:
        st.error("Kolom 'INCIDENT' tidak ditemukan. Data tidak dapat diproses.")
        return

    # Daftar kolom kepatuhan yang diharapkan
    kepatuhan_cols = ["PLATINUM", "DIAMOND", "DASHBOARD NON HVC", "MANJA"]
    available_options = [col for col in kepatuhan_cols if col in df.columns]

    if not available_options:
        st.error("Tidak ditemukan kolom kepatuhan yang relevan (PLATINUM, DIAMOND, NON HVC, MANJA) dalam dataset.")
        return

    selected_comply_col = st.selectbox("Pilih metrik kepatuhan yang ingin dianalisis:", available_options)

    def process_compliance_data(df_input, column_name, group_by_col=None):
        cols_to_use = [column_name, 'INCIDENT']
        if group_by_col:
            cols_to_use.insert(0, group_by_col)

        data = df_input[cols_to_use].copy()
        data.dropna(subset=[column_name], inplace=True)
        data[column_name] = data[column_name].astype(str).str.strip().str.upper()

        # Ambil hanya nilai valid
        data = data[data[column_name].isin(['COMPLY', 'NOT COMPLY'])]

        # Group berdasarkan INCIDENT dan ambil status terakhir (bisa disesuaikan jika perlu)
        if not group_by_col:
            data = data.sort_values(by='INCIDENT')
            data = data.groupby('INCIDENT', as_index=False).last()
        else:
            data = data.sort_values(by=[group_by_col, 'INCIDENT'])
            data = data.groupby([group_by_col, 'INCIDENT'], as_index=False).last()

        data['STATUS_KEPATUHAN'] = data[column_name]
        return data

    # --- Analisis Kepatuhan Keseluruhan ---
    st.subheader(f"📊 Ringkasan Kepatuhan Keseluruhan untuk {selected_comply_col}")

    comply_data = process_compliance_data(df, selected_comply_col)

    # Filter agar hanya INCIDENT dengan WITEL valid (agar sinkron dengan chart WITEL)
    if 'WITEL' in df.columns:
        valid_incidents = df[df['WITEL'] != 'Tidak Diketahui']['INCIDENT'].unique()
        comply_data = comply_data[comply_data['INCIDENT'].isin(valid_incidents)]

    if comply_data.empty:
        st.warning(f"Tidak ditemukan data 'COMPLY' atau 'NOT COMPLY' yang valid di kolom '{selected_comply_col}'.")
        return

    overall_summary = comply_data['STATUS_KEPATUHAN'].value_counts().reset_index()
    overall_summary.columns = ['STATUS_KEPATUHAN', 'JUMLAH']

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(overall_summary)

        total_tickets = overall_summary['JUMLAH'].sum()
        comply_tickets = overall_summary[overall_summary['STATUS_KEPATUHAN'] == 'COMPLY']['JUMLAH'].sum()
        compliance_rate = (comply_tickets / total_tickets) * 100 if total_tickets > 0 else 0
        st.metric(label="Tingkat Kepatuhan (Compliance Rate)", value=f"{compliance_rate:.2f}%")

    with col2:
        fig_pie = px.pie(
            overall_summary,
            names='STATUS_KEPATUHAN',
            values='JUMLAH',
            title=f"Proporsi COMPLY vs NOT COMPLY",
            color='STATUS_KEPATUHAN',
            color_discrete_map={'COMPLY': '#2ca02c', 'NOT COMPLY': '#d62728'},
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Analisis Kepatuhan Berdasarkan WITEL ---
    st.markdown("---")
    st.subheader(f"Analisis Kepatuhan Berdasarkan WITEL untuk {selected_comply_col}")

    if 'WITEL' in df.columns:
        witel_df_processed = process_compliance_data(df, selected_comply_col, group_by_col='WITEL')
        witel_df_processed = witel_df_processed[witel_df_processed['WITEL'] != 'Tidak Diketahui']

        witel_summary = witel_df_processed.groupby(['WITEL', 'STATUS_KEPATUHAN'])['INCIDENT'].nunique().reset_index(name='JUMLAH')

        if not witel_summary.empty:
            st.subheader("📊 Perbandingan Jumlah COMPLY vs NOT COMPLY per WITEL")
            fig_witel_grouped = px.bar(
                witel_summary,
                x='WITEL',
                y='JUMLAH',
                color='STATUS_KEPATUHAN',
                barmode='group',
                text='JUMLAH',
                title="Jumlah Tiket Patuh vs Tidak Patuh per WITEL",
                color_discrete_map={'COMPLY': '#2ca02c', 'NOT COMPLY': '#d62728'}
            )
            fig_witel_grouped.update_traces(textposition='outside')
            fig_witel_grouped.update_layout(
                xaxis_title="WITEL",
                yaxis_title="Jumlah Tiket Unik",
                legend_title="Status",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_witel_grouped, use_container_width=True)

            st.subheader("📊 Tingkat Kepatuhan (Compliance Rate) per WITEL")
            witel_total = witel_summary.groupby('WITEL')['JUMLAH'].sum().reset_index(name='TOTAL')
            witel_prop_df = witel_summary.merge(witel_total, on='WITEL')
            witel_prop_df['PERSEN'] = (witel_prop_df['JUMLAH'] / witel_prop_df['TOTAL'] * 100)

            fig_witel_percent = px.bar(
                witel_prop_df,
                x='WITEL',
                y='PERSEN',
                color='STATUS_KEPATUHAN',
                barmode='stack',
                text='PERSEN',
                title="Proporsi Kepatuhan per WITEL",
                color_discrete_map={'COMPLY': '#2ca02c', 'NOT COMPLY': '#d62728'}
            )
            fig_witel_percent.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
            fig_witel_percent.update_layout(
                xaxis_title="WITEL",
                yaxis_title="Persentase (%)",
                legend_title="Status",
                yaxis_ticksuffix="%",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_witel_percent, use_container_width=True)

    else:
        st.warning("Kolom 'WITEL' tidak ditemukan dalam dataset.")
