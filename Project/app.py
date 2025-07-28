import streamlit as st
import pandas as pd
import plotly.express as px
from halaman.h1pratinjau import show_pratinjau
from halaman.h2status import show_status
from halaman.h3owner_group import show_owner_group
from halaman.h4sumber_pelaporan import show_sumber_pelaporan
from halaman.h5segment_pelanggan import show_segment_pelanggan
from halaman.h6service_type import show_service_type
from halaman.h7prioritas import show_prioritas
from halaman.h8korelasi_ttr import show_korelasi_ttr
from halaman.h9summary_kata_kunci import show_summary_kata_kunci
from halaman.h10gamas import show_is_not_gamas

st.set_page_config(page_title="Dashboard Analisis Tiket", layout="wide")
st.title("📊 Dashboard Analisis Report TTR WSA")

st.sidebar.title("Pengaturan Data")
uploaded_file = st.sidebar.file_uploader("Unggah file CSV atau XLSX Anda", type=['csv', 'xlsx'])

# --- Fungsi untuk membaca dan membersihkan data dengan caching
@st.cache_data
def load_data_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, engine='python', encoding='latin1', on_bad_lines='skip')
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Format file tidak didukung.")
            return None

        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].fillna('Tidak Diketahui')

        if 'REPORTED DATE' in df.columns:
            df['REPORTED DATE'] = pd.to_datetime(df['REPORTED DATE'], errors='coerce')

        return df
    except Exception as e:
        st.error(f"Terjadi error saat memuat dan memproses data: {e}")
        return None

# --- Load data hanya sekali per file
if uploaded_file is not None:
    if "dataframe" not in st.session_state or st.session_state.get("filename") != uploaded_file.name:
        st.session_state["dataframe"] = load_data_file(uploaded_file)
        st.session_state["filename"] = uploaded_file.name

    df = st.session_state["dataframe"]

    if df is not None:
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
            "Klasterisasi Masalah Berdasarkan Kata Kunci dalam Kolom SUMMARY",
            "Analisis Keterkaitan IS NOT GAMAS dan Durasi Penyelesaian"
        ]
        selected_page = st.sidebar.selectbox("Pilih Analisis yang Ingin Dilihat", insight_options)

        # --- Routing halaman ke fungsi masing-masing
        if selected_page == "Pratinjau Data Report TTR WSA":
            show_pratinjau(df)
        elif selected_page == "Distribusi Tiket Berdasarkan Status":
            show_status(df)
        elif selected_page == "Owner Group dengan Tiket Terbanyak":
            show_owner_group(df)
        elif selected_page == "Sumber Pelaporan Tiket Paling Umum":
            show_sumber_pelaporan(df)
        elif selected_page == "Proporsi Tiket Berdasarkan Segmen Pelanggan":
            show_segment_pelanggan(df)
        elif selected_page == "Jenis Layanan Paling Sering Gangguan":
            show_service_type(df)
        elif selected_page == "Sebaran Tiket Berdasarkan Prioritas":
            show_prioritas(df)
        elif selected_page == "Korelasi GRUP DURASI vs COMPLY TTR":
            show_korelasi_ttr(df)
        elif selected_page == "Klasterisasi Masalah Berdasarkan Kata Kunci dalam Kolom SUMMARY":
            show_summary_kata_kunci(df)
        elif selected_page == "Analisis Keterkaitan IS NOT GAMAS dan Durasi Penyelesaian":
            show_is_not_gamas(df)
        else:
            st.warning("Halaman belum tersedia.")

else:
    st.info("Silakan unggah file CSV atau XLSX pada sidebar untuk memulai analisis.")
