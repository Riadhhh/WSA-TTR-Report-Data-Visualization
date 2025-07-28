import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

def show_peta_witel(df: pd.DataFrame):
    """
    Menampilkan analisis geospasial dari insiden per WITEL.
    Fungsi ini melakukan:
    1. Mapping dan pembersihan data WITEL.
    2. Menyediakan filter interaktif di sidebar.
    3. Menghitung agregat jumlah insiden berdasarkan filter.
    4. Memvisualisasikan data dalam bentuk peta interaktif menggunakan PyDeck
    dan tabel ringkasan.
    """
    st.header("🗺️ Peta Sebaran Insiden per WITEL")

    # --- Konfigurasi Koordinat WITEL ---
    koordinat_witel = {
        "JAMBI": [103.6131, -1.6101],
        "RIAU": [101.4445, 0.5071],
        "SUMATERA BARAT": [100.3639, -0.9492],
        "KEPULAUAN RIAU": [104.4421, 0.9116],
        "ACEH": [95.3222, 5.5527],
        "BANDAR LAMPUNG": [105.2667, -5.4167],
        "MEDAN": [98.6769, 3.5897],
        "SUMATERA UTARA": [99.1333, 2.1167],
        "SUMATERA SELATAN": [104.7458, -2.9909],
        "BANGKA BELITUNG": [106.1167, -2.7333],
        "BENGKULU": [102.2655, -3.8004],
    }

    # --- Mapping Nama WITEL ---
    mapping_witel = {
        "JAMBI": "JAMBI", "RIDAR": "RIAU", "SUMBAR": "SUMATERA BARAT",
        "RIKEP": "KEPULAUAN RIAU", "ACEH": "ACEH", "LAMPUNG": "BANDAR LAMPUNG",
        "MEDAN": "MEDAN", "SUMUT": "SUMATERA UTARA", "SUMSEL": "SUMATERA SELATAN",
        "BABEL": "BANGKA BELITUNG", "BENGKULU": "BENGKULU",
    }

    # Pastikan kolom 'WITEL' ada sebelum melakukan mapping
    if 'WITEL' not in df.columns:
        st.error("Kolom 'WITEL' tidak ditemukan dalam dataset.")
        return

    df['WITEL_MAP'] = df['WITEL'].map(mapping_witel)
    df_filtered = df.dropna(subset=['WITEL_MAP'])
    df_filtered = df_filtered[df_filtered['WITEL_MAP'].isin(koordinat_witel.keys())]

    st.sidebar.subheader("🔎 Jenis Analisis Peta")
    mode = st.sidebar.selectbox("Pilih Mode Analisis:", [
        "Jumlah Total Insiden",
        "Jumlah Insiden Berdasarkan SERVICE TYPE",
        "Jumlah Insiden Berdasarkan STATUS"
    ])

    data = pd.DataFrame()

    if mode == "Jumlah Total Insiden":
        data = df_filtered.groupby('WITEL_MAP')['INCIDENT'].count().reset_index(name='JUMLAH')

    elif mode == "Jumlah Insiden Berdasarkan SERVICE TYPE":
        if 'SERVICE TYPE' in df_filtered.columns:
            service_types = df_filtered['SERVICE TYPE'].dropna().unique()
            if len(service_types) > 0:
                selected_service = st.sidebar.selectbox("Pilih SERVICE TYPE:", service_types)
                data = df_filtered[df_filtered['SERVICE TYPE'] == selected_service].groupby('WITEL_MAP')['INCIDENT'].count().reset_index(name='JUMLAH')
            else:
                st.warning("Tidak ada data 'SERVICE TYPE' yang valid untuk difilter.")
        else:
            st.error("Kolom 'SERVICE TYPE' tidak ditemukan.")

    elif mode == "Jumlah Insiden Berdasarkan STATUS":
        if 'STATUS' in df_filtered.columns:
            statuses = df_filtered['STATUS'].dropna().unique()
            if len(statuses) > 0:
                selected_status = st.sidebar.selectbox("Pilih STATUS:", statuses)
                data = df_filtered[df_filtered['STATUS'] == selected_status].groupby('WITEL_MAP')['INCIDENT'].count().reset_index(name='JUMLAH')
            else:
                st.warning("Tidak ada data 'STATUS' yang valid untuk difilter.")
        else:
            st.error("Kolom 'STATUS' tidak ditemukan.")

    if data.empty:
        st.warning("Tidak ada data untuk ditampilkan dengan filter yang dipilih. Silakan coba filter lain.")
        return

    # --- Tambahkan Koordinat ke Data Agregat ---
    data['LON'] = data['WITEL_MAP'].apply(lambda x: koordinat_witel[x][0])
    data['LAT'] = data['WITEL_MAP'].apply(lambda x: koordinat_witel[x][1])

    # --- Transformasi Logaritmik untuk Skala Lingkaran ---
    data['JUMLAH_LOG'] = np.log1p(data['JUMLAH'])  # log(1 + x) untuk menghindari log(0)

    # --- Tampilkan Tabel Ringkasan ---
    st.subheader("📋 Tabel Ringkasan Jumlah Insiden per WITEL")
    st.dataframe(data[['WITEL_MAP', 'JUMLAH']].sort_values(by='JUMLAH', ascending=False).reset_index(drop=True))

    # --- Peta Interaktif ---
    st.subheader("🌍 Peta Interaktif Jumlah Insiden")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data,
        get_position='[LON, LAT]',
        get_radius="5000 + JUMLAH_LOG * 10000",  # Radius dasar + skala logaritmik
        get_fill_color='[200, 30, 0, 160]',
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        longitude=101.5,
        latitude=0.5,
        zoom=4.5,
        pitch=45
    )

    tooltip = {
        "html": "<b>{WITEL_MAP}</b><br/>Jumlah Insiden: {JUMLAH}",
        "style": {
            "backgroundColor": "steelblue",
            "color": "white",
            "border-radius": "5px",
            "padding": "5px"
        }
    }

    r = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style='mapbox://styles/mapbox/light-v9'
    )
    st.pydeck_chart(r)
