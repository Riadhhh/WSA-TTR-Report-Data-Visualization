import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import plotly.express as px

def show_peta_witel(df: pd.DataFrame):
    st.header("🌍️ Peta Sebaran Insiden per WITEL")

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

    mapping_witel = {
        "JAMBI": "JAMBI", "RIDAR": "RIAU", "SUMBAR": "SUMATERA BARAT",
        "RIKEP": "KEPULAUAN RIAU", "ACEH": "ACEH", "LAMPUNG": "BANDAR LAMPUNG",
        "MEDAN": "MEDAN", "SUMUT": "SUMATERA UTARA", "SUMSEL": "SUMATERA SELATAN",
        "BABEL": "BANGKA BELITUNG", "BENGKULU": "BENGKULU",
    }

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

    # Filter sesuai mode
    if mode == "Jumlah Insiden Berdasarkan SERVICE TYPE" and 'SERVICE TYPE' in df_filtered.columns:
        service_types = df_filtered['SERVICE TYPE'].dropna().unique()
        if len(service_types) > 0:
            selected_service = st.sidebar.selectbox("Pilih SERVICE TYPE:", service_types)
            df_filtered = df_filtered[df_filtered['SERVICE TYPE'] == selected_service]

    elif mode == "Jumlah Insiden Berdasarkan STATUS" and 'STATUS' in df_filtered.columns:
        statuses = df_filtered['STATUS'].dropna().unique()
        if len(statuses) > 0:
            selected_status = st.sidebar.selectbox("Pilih STATUS:", statuses)
            df_filtered = df_filtered[df_filtered['STATUS'] == selected_status]

    # Agregasi data untuk peta
    data = df_filtered.groupby('WITEL_MAP')['INCIDENT'].count().reset_index(name='JUMLAH')
    if data.empty:
        st.warning("Tidak ada data untuk ditampilkan dengan filter yang dipilih. Silakan coba filter lain.")
        return

    data['LON'] = data['WITEL_MAP'].apply(lambda x: koordinat_witel[x][0])
    data['LAT'] = data['WITEL_MAP'].apply(lambda x: koordinat_witel[x][1])
    data['JUMLAH_LOG'] = np.log1p(data['JUMLAH'])
    min_jumlah = data['JUMLAH'].min()
    max_jumlah = data['JUMLAH'].max()
    data['NORMALIZED'] = (data['JUMLAH'] - min_jumlah) / (max_jumlah - min_jumlah + 1e-9)

    def gradasi_biru_kuning_merah(x):
        if x <= 0.5:
            ratio = x / 0.5
            r = int(255 * ratio)
            g = int(255 * ratio)
            b = int(255 * (1 - ratio))
        else:
            ratio = (x - 0.5) / 0.5
            r = 255
            g = int(255 * (1 - ratio))
            b = 0
        return [r, g, b, 200]

    data['COLOR'] = data['NORMALIZED'].apply(gradasi_biru_kuning_merah)

    st.subheader("📋 Tabel Jumlah Insiden per WITEL")
    st.dataframe(data[['WITEL_MAP', 'JUMLAH']].sort_values(by='JUMLAH', ascending=False).reset_index(drop=True))

    st.subheader("🌍 Peta Interaktif Jumlah Insiden")
    layer = pdk.Layer(
        "ColumnLayer",
        data=data,
        get_position='[LON, LAT]',
        get_elevation='JUMLAH_LOG * 10500',
        elevation_scale=1,
        radius=15000,
        get_fill_color='COLOR',
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
        map_style="https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json"
    )
    st.pydeck_chart(r)

    # Tabel WORKZONE - WITEL - JUMLAH
    workzone_summary = (
        df_filtered.groupby(['WORKZONE', 'WITEL_MAP'])['INCIDENT']
        .count()
        .reset_index(name='JUMLAH')
        .sort_values(by='JUMLAH', ascending=False)
    )
    st.subheader("📋 Tabel Jumlah WORKZONE - WITEL")
    st.dataframe(workzone_summary.reset_index(drop=True))

    st.subheader(":bar_chart: Jumlah Insiden Berdasarkan WORKZONE")
    if 'WORKZONE' in df_filtered.columns:
        top_n = st.slider("Tampilkan Top N WORKZONE", min_value=3, max_value=20, value=10)
        top_workzones = (
            df_filtered.groupby('WORKZONE')['INCIDENT']
            .count()
            .reset_index(name='JUMLAH')
            .sort_values(by='JUMLAH', ascending=False)
            .head(top_n)
        )
        fig = px.bar(
            top_workzones,
            x='JUMLAH',
            y='WORKZONE',
            orientation='h',
            color='JUMLAH',
            color_continuous_scale='Bluered_r',
            labels={'JUMLAH': 'Jumlah Insiden'},
            title=f"Top {top_n} WORKZONE Berdasarkan Jumlah Insiden"
        )
        fig.update_layout(
            yaxis=dict(dtick=1),
            height=top_n * 30 + 100
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Kolom 'WORKZONE' tidak ditemukan dalam dataset.")
