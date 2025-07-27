import streamlit as st
import pandas as pd
import plotly.express as px

def show_korelasi_ttr(df: pd.DataFrame):
    st.header("📈 Analisis Korelasi: GRUP DURASI vs Kepatuhan TTR")

    duration_col_name = 'GRUP DURASI  SISA ORDER TTR OPEN'
    comply_columns = [col for col in df.columns if 'COMPLY' in col.upper()]

    if duration_col_name not in df.columns:
        st.error(f"Kolom '{duration_col_name}' tidak ditemukan.")
        return
    if len(comply_columns) == 0:
        st.error("Kolom COMPLY tidak ditemukan.")
        return

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
        return

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
    st.subheader("📊 Distribusi Kepatuhan per Grup Durasi (Jumlah Tiket Unik)")
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

    # --- Visualisasi 2: 100% Stacked Bar Chart (Proporsi)
    total_per_durasi = grouped.groupby('GRUP_DURASI_LABEL')['JUMLAH'].sum().reset_index(name='TOTAL')
    prop_df = grouped.merge(total_per_durasi, on='GRUP_DURASI_LABEL')
    prop_df['PERSEN'] = (prop_df['JUMLAH'] / prop_df['TOTAL'] * 100)

    st.subheader("📊 Proporsi Kepatuhan per Grup Durasi (%)")
    fig2 = px.bar(
        prop_df,
        x='GRUP_DURASI_LABEL',
        y='PERSEN',
        color='STATUS_KEPATUHAN',
        text='PERSEN',
        barmode='stack',
        color_discrete_map={'COMPLY': '#2ca02c', 'NON COMPLY': '#d62728'}
    )
    fig2.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
    fig2.update_layout(
        title="Persentase Kepatuhan per Grup Durasi",
        xaxis_title=f"Grup Durasi ({kategori_label})",
        yaxis_title="Persentase Kepatuhan (%)",
        legend_title="Status",
        height=500,
        yaxis_ticksuffix="%"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # --- Visualisasi 3: Tren Non-Comply
    st.subheader("📉 Tren Tingkat Kegagalan (Non-Compliance Rate)")
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
    **Interpretasi:** Diagram garis ini menunjukkan tren tingkat kegagalan.
    Jika garis cenderung naik, artinya semakin lama durasi penyelesaian tiket, semakin tinggi pula kemungkinan tiket tersebut gagal memenuhi target SLA.
    """)
