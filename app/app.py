import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
from wordcloud import WordCloud
from collections import Counter
import re

st.set_page_config(page_title="Dashboard Analisis Tiket", layout="wide")
st.title("📊 Dashboard Analisis Report TTR WSA")

st.sidebar.title("Pengaturan Data")

# Upload file
uploaded_file = st.sidebar.file_uploader("Unggah file CSV atau XLSX Anda", type=['csv', 'xlsx'])

def load_data(uploaded_file):
    """Memuat data dari file yang diunggah dan melakukan pembersihan dasar."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, engine='python', encoding='latin1', on_bad_lines='skip')
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Format file tidak didukung. Harap unggah file CSV atau XLSX.")
            return None

        # Isi NaN pada kolom object dengan 'Tidak Diketahui'
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].fillna('Tidak Diketahui')

        return df
    except Exception as e:
        st.error(f"Terjadi error saat memuat dan memproses data: {e}")
        return None

# Load data
if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is not None:
        # Konversi kolom tanggal jika tersedia
        if 'REPORTED DATE' in df.columns:
            df['REPORTED DATE'] = pd.to_datetime(df['REPORTED DATE'], errors='coerce')

        # Navigasi Sidebar
        st.sidebar.title("Navigasi Analisis")
        insight_options = [
            "Pratinjau Data Report TTR WSA",
            "Distribusi Tiket Berdasarkan Status",
            "Owner Group dengan Tiket Terbanyak",
            "Sumber Pelaporan Tiket Paling Umum",
            "Proporsi Tiket Berdasarkan Segmen Pelanggan",
            "Jenis Layanan Paling Sering Gangguan",
            "Sebaran Tiket Berdasarkan Prioritas",
            "Korelasi GRUP DURASI vs COMPLY TTR",
            "Klasterisasi Masalah Berdasarkan Kata Kunci dalam Kolom SUMMARY"
        ]
        selected_insight = st.sidebar.selectbox("Pilih Analisis yang Ingin Dilihat", insight_options)

        # Halaman 1: Pratinjau Data Report TTR WSA
        if selected_insight == "Pratinjau Data Report TTR WSA": 
            st.subheader("Pratinjau Data Mentah Insiden")
            
            st.write(f"Jumlah Baris: **{df.shape[0]}**")
            st.write(f"Jumlah Kolom: **{df.shape[1]}**")
            
            st.dataframe(df.head(100))
            
            st.subheader("Informasi Kolom Dataset")
            st.write("Berikut adalah daftar kolom dan tipe datanya:")
            cols_df = pd.DataFrame({
                "Nama Kolom": df.columns,
                "Tipe Data": df.dtypes.astype(str)
            })
            st.dataframe(cols_df)

        # Halaman 2: Distribusi Tiket Berdasarkan Status
        elif selected_insight == "Distribusi Tiket Berdasarkan Status":  
            st.header("Analisis Distribusi Tiket Berdasarkan Status")
            
            if 'STATUS' in df.columns and 'INCIDENT' in df.columns:
                # Hapus baris dengan status 'Tidak Diketahui'
                filtered_df = df[df['STATUS'] != 'Tidak Diketahui']

                # Hitung jumlah insiden (baris) per status
                status_counts = filtered_df.groupby('STATUS')['INCIDENT'].count().sort_values(ascending=False)

                st.subheader("Tabel Jumlah Tiket per Status")
                st.dataframe(status_counts)

                # Ambil jumlah status unik (untuk slider)
                unique_status = filtered_df['STATUS'].nunique()
                min_slider = min(3, unique_status)

                # Slider untuk memilih Top N Status
                top_n = st.slider(
                    "Pilih jumlah Top 'Status' yang ingin ditampilkan:",
                    min_value=min_slider,
                    max_value=unique_status,
                    value=min(4, unique_status)
                )

                # Ambil Top N status
                top_status_counts = status_counts.nlargest(top_n)

                # Ubah menjadi dataframe untuk plotly
                status_df = top_status_counts.reset_index()
                status_df.columns = ['STATUS', 'JUMLAH TIKET']

                # ------------------- DIAGRAM BATANG VERTIKAL (Plotly) -------------------
                st.subheader("Diagram Batang Vertikal (Plotly Bar Chart)")
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

                # ------------------- DIAGRAM BATANG HORIZONTAL (Plotly) -------------------
                st.subheader("Diagram Batang Horizontal (Plotly Horizontal Bar Chart)")
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

                # ------------------- PIE CHART (Plotly) -------------------
                st.subheader("Diagram Pie (Proporsi Tiket per Status)")
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


        # Halaman 3: Owner Group Terbanyak
        elif selected_insight == "Owner Group dengan Tiket Terbanyak":  
            st.header("Analisis Owner Group dengan Tiket Terbanyak")
            
            if 'OWNER GROUP' in df.columns and 'INCIDENT' in df.columns:
                # Filter data: buang 'Tidak Diketahui'
                filtered_df = df[df['OWNER GROUP'] != 'Tidak Diketahui']

                # Hitung jumlah tiket per owner group
                owner_group_counts = filtered_df.groupby('OWNER GROUP')['INCIDENT'].count().sort_values(ascending=False)

                st.subheader("Tabel Jumlah Tiket per Owner Group")
                st.dataframe(owner_group_counts)

                unique_owner_groups = filtered_df['OWNER GROUP'].nunique()
                min_slider = min(5, unique_owner_groups)

                # Slider untuk Top N
                top_n = st.slider(
                    "Pilih jumlah Top 'Owner Group' yang ingin ditampilkan:",
                    min_value=min_slider,
                    max_value=unique_owner_groups,
                    value=min(10, unique_owner_groups)
                )

                # Ambil Top N
                top_owner_group_counts = owner_group_counts.nlargest(top_n)

                # Siapkan dataframe untuk plotly
                owner_group_df = top_owner_group_counts.reset_index()
                owner_group_df.columns = ['OWNER GROUP', 'JUMLAH TIKET']

                # ------------------- DIAGRAM BATANG VERTIKAL -------------------
                st.subheader("Diagram Batang Vertikal (Plotly Bar Chart)")
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

                # ------------------- DIAGRAM BATANG HORIZONTAL -------------------
                st.subheader("Diagram Batang Horizontal (Plotly Horizontal Bar Chart)")
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

                # ------------------- DOT PLOT (Plotly Scatter) -------------------
                st.subheader("Dot Plot (Perbandingan Owner Group)")

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


        # Halaman 4: Sumber Pelaporan Tiket
        elif selected_insight == "Sumber Pelaporan Tiket Paling Umum":
            st.header("Analisis Sumber Pelaporan Tiket Paling Umum")
            
            if 'SOURCE TICKET' in df.columns and 'INCIDENT' in df.columns:
                filtered_df = df[df['SOURCE TICKET'] != 'Tidak Diketahui']

                source_ticket_counts = filtered_df.groupby('SOURCE TICKET')['INCIDENT'].count().sort_values(ascending=False)

                st.subheader("Tabel Jumlah Tiket per Sumber Pelaporan")
                st.dataframe(source_ticket_counts)
                st.info("Hanya ada satu kategori teknologi yang valid, visualisasi tidak ditampilkan.")
            else:
                st.warning("Kolom 'SOURCE TICKET' atau 'INCIDENT' tidak ditemukan dalam dataset.")


        # Halaman 5: Proporsi Segmen Pelanggan
        elif selected_insight == "Proporsi Tiket Berdasarkan Segmen Pelanggan":
            st.header("Analisis Proporsi Tiket Berdasarkan Segmen Pelanggan")

            if 'CUSTOMER SEGMENT' in df.columns and 'INCIDENT' in df.columns:
                filtered_df = df[df['CUSTOMER SEGMENT'] != 'Tidak Diketahui']
                segment_counts = filtered_df.groupby('CUSTOMER SEGMENT')['INCIDENT'].count().sort_values(ascending=False)

                st.subheader("Tabel Jumlah Tiket per Segmen Pelanggan")
                st.dataframe(segment_counts)
                st.info("Hanya ada satu kategori teknologi yang valid, visualisasi tidak ditampilkan.")
            else:
                st.warning("Kolom 'CUSTOMER SEGMENT' atau 'INCIDENT' tidak ditemukan dalam dataset.")


        # Halaman 6: Jenis Layanan Paling Sering Gangguan
        elif selected_insight == "Jenis Layanan Paling Sering Gangguan":
            st.header("Analisis Jenis Layanan Paling Sering Mengalami Gangguan")

            if 'SERVICE TYPE' in df.columns and 'INCIDENT' in df.columns:
                filtered_df = df[df['SERVICE TYPE'] != 'Tidak Diketahui']

                service_type_counts = filtered_df.groupby('SERVICE TYPE')['INCIDENT'].count().sort_values(ascending=False)

                st.subheader("Tabel Jumlah Gangguan per Jenis Layanan")
                st.dataframe(service_type_counts)

                unique_service_types = filtered_df['SERVICE TYPE'].nunique()
                min_slider = min(1, unique_service_types)

                top_n = st.slider(
                    "Pilih jumlah Top 'Jenis Layanan' yang ingin ditampilkan:",
                    min_value=min_slider,
                    max_value=unique_service_types,
                    value=min(3, unique_service_types)
                )
                top_service_counts = service_type_counts.nlargest(top_n)

                service_df = top_service_counts.reset_index()
                service_df.columns = ['SERVICE TYPE', 'JUMLAH GANGGUAN']

                # ------------------- DIAGRAM BATANG VERTIKAL -------------------
                st.subheader("Diagram Batang Vertikal (Plotly Bar Chart)")
                st.write(f"Visualisasi ini mengurutkan {top_n} Jenis Layanan yang paling sering mengalami gangguan.")
                fig_bar = px.bar(
                    service_df,
                    x='SERVICE TYPE',
                    y='JUMLAH GANGGUAN',
                    color='SERVICE TYPE',
                    text='JUMLAH GANGGUAN',
                    title=f"Top {top_n} Jenis Layanan Paling Sering Gangguan"
                )
                fig_bar.update_traces(textposition='outside')
                fig_bar.update_layout(
                    xaxis_title="Jenis Layanan",
                    yaxis_title="Jumlah Gangguan",
                    showlegend=False,
                    height=600
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                # ------------------- DIAGRAM BATANG HORIZONTAL -------------------
                st.subheader("Diagram Batang Horizontal (Plotly Horizontal Bar Chart)")
                fig_bar_h = px.bar(
                    service_df,
                    x='JUMLAH GANGGUAN',
                    y='SERVICE TYPE',
                    orientation='h',
                    color='SERVICE TYPE',
                    text='JUMLAH GANGGUAN',
                    title=f"Top {top_n} Jenis Layanan Paling Sering Gangguan (Horizontal)"
                )
                fig_bar_h.update_traces(textposition='outside')
                fig_bar_h.update_layout(
                    xaxis_title="Jumlah Gangguan",
                    yaxis_title="Jenis Layanan",
                    showlegend=False,
                    height=500
                )
                st.plotly_chart(fig_bar_h, use_container_width=True)

                # ------------------- FACET BAR CHART: Jenis Layanan per Status -------------------
                if 'STATUS' in df.columns:
                    st.subheader("Diagram Bar Terpisah (Facet) Berdasarkan Status Tiket")

                    top_services = top_service_counts.index.tolist()
                    facet_df = df[df['SERVICE TYPE'].isin(top_services)]
                    facet_df = facet_df[facet_df['STATUS'] != 'Tidak Diketahui']

                    grouped_facet = facet_df.groupby(['SERVICE TYPE', 'STATUS'])['INCIDENT'].count().reset_index()

                    fig_facet = px.bar(
                        grouped_facet,
                        x='SERVICE TYPE',
                        y='INCIDENT',
                        color='SERVICE TYPE',
                        facet_col='STATUS',
                        text='INCIDENT',
                        title=f"Jumlah Tiket per Jenis Layanan Berdasarkan Status Tiket (Top {top_n})"
                    )

                    fig_facet.update_traces(textposition='outside')
                    fig_facet.update_layout(
                        height=600,
                        showlegend=False,
                        yaxis_title="Jumlah Tiket",
                        xaxis_title="Jenis Layanan",
                        margin=dict(t=60)
                    )

                    st.plotly_chart(fig_facet, use_container_width=True)
                else:
                    st.warning("Kolom 'STATUS' tidak ditemukan. Tidak dapat menampilkan facet chart.")
            else:
                st.warning("Kolom 'SERVICE TYPE' atau 'INCIDENT' tidak ditemukan dalam dataset.")


        # Halaman 7: Sebaran Tiket Berdasarkan Prioritas
        elif selected_insight == "Sebaran Tiket Berdasarkan Prioritas":
            st.header("Sebaran Tiket Berdasarkan Prioritas (REPORTED PRIORITY)")

            if 'REPORTED PRIORITY' in df.columns and 'INCIDENT' in df.columns and 'REPORTED DATE' in df.columns:
                analysis_df = df.copy()
                analysis_df['REPORTED PRIORITY'] = analysis_df['REPORTED PRIORITY'].fillna('Tidak Diketahui')

                analysis_df['REPORTED DATE'] = pd.to_datetime(analysis_df['REPORTED DATE'], errors='coerce')
                analysis_df['TANGGAL'] = analysis_df['REPORTED DATE'].dt.date

                priority_counts = analysis_df.groupby('REPORTED PRIORITY')['INCIDENT'].count().sort_values(ascending=False)

                st.subheader("Tabel Jumlah Tiket per Prioritas")
                st.dataframe(priority_counts)

                priority_df = priority_counts.reset_index()
                priority_df.columns = ['REPORTED PRIORITY', 'JUMLAH TIKET']

                # ---------------------- DIAGRAM BATANG VERTIKAL ----------------------
                st.subheader("Diagram Batang Vertikal (Plotly Bar Chart)")
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

                # ---------------------- DIAGRAM BATANG HORIZONTAL ----------------------
                st.subheader("Diagram Batang Horizontal (Plotly Bar Chart Horizontal)")
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

                # ---------------------- PIE CHART (Exploded Style) ----------------------
                st.subheader("Diagram Pie (Plotly Pie Chart)")
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
                st.warning("Kolom 'REPORTED PRIORITY', 'INCIDENT' tidak ditemukan dalam dataset.")

        # Halaman 8: Korelasi GRUP DURASI vs COMPLY TTR
        elif selected_insight == "Korelasi GRUP DURASI vs COMPLY TTR":
            st.header("Analisis Korelasi: GRUP DURASI vs Kepatuhan TTR")

            # Pastikan nama kolom sesuai dengan file (dengan spasi ganda)
            duration_col_name = 'GRUP DURASI  SISA ORDER TTR OPEN'
            comply_columns = [col for col in df.columns if 'COMPLY' in col.upper()]

            if duration_col_name not in df.columns:
                st.error(f"Kolom '{duration_col_name}' tidak ditemukan.")
                st.stop()
            if len(comply_columns) == 0:
                st.error("Kolom COMPLY tidak ditemukan.")
                st.stop()

            selected_comply_col = st.selectbox("Pilih metrik COMPLY yang ingin dianalisis:", comply_columns)

            # --- Mapping Durasi Berdasarkan Jenis COMPLY ---
            mapping_durasi = {}
            kategori_label = ""
            durasi_order = []

            if "NON HVC" in selected_comply_col.upper():
                mapping_durasi = {
                    1: '<= 3 JAM', 2: '3 - 6 JAM', 3: '6 - 12 JAM',
                    4: '12 - 24 JAM', 5: '24 - 36 JAM', 6: '36 - 48 JAM',
                    7: '48 - 72 JAM', 8: '> 72 JAM'
                }
                kategori_label = "Marking 36 Jam Non HVC"
                durasi_order = list(mapping_durasi.values())

            elif "PLATINUM" in selected_comply_col.upper():
                mapping_durasi = {
                    1: '<= 1 JAM', 2: '1 - 2 JAM', 3: '2 - 3 JAM',
                    4: '3 - 6 JAM', 5: '> 6 JAM'
                }
                kategori_label = "Marking Platinum"
                durasi_order = list(mapping_durasi.values())

            elif "DIAMOND" in selected_comply_col.upper() or "3 JAM MANJA" in selected_comply_col.upper():
                mapping_durasi = {
                    1: '<= 1 JAM', 2: '1 - 2 JAM', 3: '2 - 3 JAM', 4: '> 3 JAM'
                }
                kategori_label = "Marking Diamond"
                durasi_order = list(mapping_durasi.values())
            
            else:
                st.warning("Tidak ada mapping durasi spesifik untuk kolom COMPLY ini. Menggunakan urutan data asli.")
                kategori_label = "Default"


            # --- Filter & Mapping ---
            df_filtered = df[[duration_col_name, selected_comply_col, 'INCIDENT']].copy()
            df_filtered.dropna(subset=[duration_col_name, selected_comply_col, 'INCIDENT'], inplace=True)
            
            df_filtered['GRUP_DURASI_LABEL'] = df_filtered[duration_col_name]
            if pd.api.types.is_numeric_dtype(df_filtered[duration_col_name]) and kategori_label != "Default":
                df_filtered['GRUP_DURASI_LABEL'] = df_filtered[duration_col_name].map(mapping_durasi)

            if not durasi_order:
                durasi_order = sorted(df_filtered['GRUP_DURASI_LABEL'].dropna().unique())

            df_filtered.dropna(subset=['GRUP_DURASI_LABEL'], inplace=True)

            def normalize_comply(val):
                val_str = str(val).strip().upper()
                return 'COMPLY' if val_str in ['TRUE', 'YA', 'YES', '1', 'T', 'Y', '✓', 'COMPLY'] else 'NON COMPLY'

            df_filtered['STATUS_KEPATUHAN'] = df_filtered[selected_comply_col].apply(normalize_comply)

            # --- Grouping Tiket Unik ---
            grouped = (
                df_filtered
                .groupby(['GRUP_DURASI_LABEL', 'STATUS_KEPATUHAN'])['INCIDENT']
                .nunique()
                .reset_index(name='JUMLAH')
            )
            grouped['GRUP_DURASI_LABEL'] = pd.Categorical(grouped['GRUP_DURASI_LABEL'], categories=durasi_order, ordered=True)
            grouped.sort_values('GRUP_DURASI_LABEL', inplace=True)

            if grouped.empty:
                st.error("❗ Tidak ada data valid untuk ditampilkan setelah pemrosesan.")
                st.stop()

            # --- Penjelasan ---
            st.info(f"""
            **Penjelasan:**

            - **COMPLY** = Tiket diselesaikan sesuai target SLA.
            - **NON COMPLY** = Tiket melebihi batas waktu SLA.
            - Grup durasi ditentukan berdasarkan jenis COMPLY yang dipilih:
            - `{selected_comply_col}` → **{kategori_label}**
            - Diagram pertama = jumlah tiket, diagram kedua = persentase kepatuhan.
            """)

            # --- Visualisasi 1: Stacked Bar Chart (Absolut) ---
            st.subheader("Distribusi Kepatuhan per Grup Durasi (Jumlah Tiket Unik)")
            fig1 = px.bar(
                grouped,
                x='GRUP_DURASI_LABEL',
                y='JUMLAH',
                color='STATUS_KEPATUHAN',
                text='JUMLAH',
                barmode='stack',
                color_discrete_map={'COMPLY': '#2ca02c', 'NON COMPLY': '#d62728'}
            )
            fig1.update_layout(
                title=f"Jumlah Tiket COMPLY vs NON COMPLY per Grup Durasi",
                xaxis_title=f"Grup Durasi ({kategori_label})",
                yaxis_title="Jumlah Tiket Unik",
                legend_title="Status",
                height=500
            )
            st.plotly_chart(fig1, use_container_width=True)

            # --- Persiapan Data untuk Persentase ---
            total_per_durasi = grouped.groupby('GRUP_DURASI_LABEL')['JUMLAH'].sum().reset_index(name='TOTAL')
            prop_df = grouped.merge(total_per_durasi, on='GRUP_DURASI_LABEL')
            prop_df['PERSEN'] = (prop_df['JUMLAH'] / prop_df['TOTAL'] * 100)

            # --- [FIXED] Visualisasi 2: 100% Stacked Bar Chart (Metode Manual) ---
            st.subheader("Proporsi Kepatuhan per Grup Durasi (%)")
            fig2 = px.bar(
                prop_df,
                x='GRUP_DURASI_LABEL',
                y='PERSEN', # Menggunakan kolom persentase yang sudah dihitung
                color='STATUS_KEPATUHAN',
                text='PERSEN', # Menampilkan nilai persentase
                barmode='stack',
                color_discrete_map={'COMPLY': '#2ca02c', 'NON COMPLY': '#d62728'}
            )
            fig2.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
            fig2.update_layout(
                title=f"Persentase Kepatuhan per Grup Durasi",
                xaxis_title=f"Grup Durasi ({kategori_label})",
                yaxis_title="Persentase Kepatuhan (%)",
                legend_title="Status",
                height=500,
                yaxis_ticksuffix="%" # Menambahkan simbol % pada sumbu Y
            )
            st.plotly_chart(fig2, use_container_width=True)

            # --- Visualisasi 3: Line Chart Tren Non-Compliance ---
            st.subheader("Tren Tingkat Kegagalan (Non-Compliance Rate)")
            non_comply_df = prop_df[prop_df['STATUS_KEPATUHAN'] == 'NON COMPLY'].copy()

            fig3 = px.line(
                non_comply_df,
                x='GRUP_DURASI_LABEL',
                y='PERSEN',
                text='PERSEN',
                markers=True,
                title="Tren Persentase NON COMPLY di Setiap Grup Durasi"
            )
            fig3.update_traces(texttemplate='%{text:.1f}%', textposition='top center')
            fig3.update_layout(
                xaxis_title=f"Grup Durasi ({kategori_label})",
                yaxis_title="Persentase NON COMPLY (%)",
                height=400,
                yaxis_range=[0, 105]
            )
            st.plotly_chart(fig3, use_container_width=True)
            st.info("""
            **Interpretasi:** Diagram garis ini secara spesifik menunjukkan tren tingkat kegagalan. Jika garis cenderung naik, artinya semakin lama durasi penyelesaian tiket, semakin tinggi pula kemungkinan tiket tersebut gagal memenuhi target SLA.
            """)

        # Halaman 9: Klasterisasi Masalah Berdasarkan Kata Kunci dalam Kolom SUMMARY
        elif selected_insight == "Klasterisasi Masalah Berdasarkan Kata Kunci dalam Kolom SUMMARY":
            st.header("Analisis Topik Masalah dari Ringkasan Laporan (SUMMARY)")

            if 'SUMMARY' not in df.columns:
                st.warning("Kolom 'SUMMARY' tidak ditemukan dalam dataset.")
                st.stop()

            st.write("""
            Anda dapat menentukan sendiri daftar **kata kunci penting** yang ingin dianalisis dari kolom 'SUMMARY'.
            Analisis ini akan menampilkan **frekuensi kemunculan kata-kata tersebut** dalam bentuk Word Cloud dan Bar Chart.
            """)

            # --- Sidebar Pengaturan ---
            st.sidebar.subheader("Pengaturan Kata Kunci")
            keyword_list_input = st.sidebar.text_area(
                "Masukkan daftar kata kunci yang ingin dianalisis (dipisahkan koma):",
                "jaringan, lelet, lambat, sinyal, error, wifi, down, buffering"
            )

            max_words = st.sidebar.slider("Jumlah kata kunci maksimum yang ditampilkan:", 5, 50, 20)
            min_freq = st.sidebar.number_input("Minimal frekuensi kata:", 1, 100, 2)

            # --- Preprocessing Teks Summary ---
            text_summary = ' '.join(df['SUMMARY'].dropna().astype(str)).lower()
            text_summary = re.sub(r'[^a-z\s]', '', text_summary)
            all_words = text_summary.split()

            # --- Whitelist Kata Kunci ---
            whitelist_keywords = [kw.strip() for kw in keyword_list_input.lower().split(',') if kw.strip()]
            if not whitelist_keywords:
                st.warning("Mohon masukkan minimal satu kata kunci yang valid.")
                st.stop()

            filtered = [word for word in all_words if word in whitelist_keywords]
            word_counts = Counter(filtered)
            selected_words = [(w, c) for w, c in word_counts.items() if c >= min_freq]
            selected_words = sorted(selected_words, key=lambda x: x[1], reverse=True)[:max_words]

            if not selected_words:
                st.info("Tidak ada kata dari whitelist yang ditemukan dalam data.")
                st.stop()

            # --- Word Cloud ---
            st.subheader("☁️ Word Cloud Berdasarkan Kata Kunci")
            wordcloud = WordCloud(
                width=1200,
                height=600,
                background_color='white',
                colormap='winter',
                max_words=max_words
            ).generate_from_frequencies(dict(selected_words))

            fig_wc, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig_wc)

            # --- Bar Chart Frekuensi Kata ---
            st.subheader("📊 Frekuensi Kata Kunci")
            df_keyword = pd.DataFrame(selected_words, columns=['Kata Kunci', 'Frekuensi'])
            fig_bar = px.bar(
                df_keyword.sort_values(by='Frekuensi', ascending=True),
                x='Frekuensi',
                y='Kata Kunci',
                orientation='h',
                text='Frekuensi'
            )
            fig_bar.update_layout(
                height=max(400, len(df_keyword) * 20),
                xaxis_title="Jumlah Kemunculan",
                yaxis_title="Kata Kunci"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # --- Ringkasan ---
            st.markdown("🔍 **Top 5 Kata Kunci Teratas:**")
            top5 = ', '.join([w for w, _ in selected_words[:5]])
            st.success(top5)




else:
    st.info("Silakan unggah file CSV atau XLSX pada sidebar untuk memulai analisis.")
