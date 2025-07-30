import streamlit as st
import pandas as pd
import plotly.express as px
import re

def extract_solution_info(text: str):
    if not isinstance(text, str):
        return None, None
        
    text_upper = text.upper()
    keywords = ["INDIHOME", "GAMAS", "SIP_TRUNK"]
    
    for keyword in keywords:
        if keyword in text_upper:
            match = re.search(rf'{keyword}\b\s*[^\w\s]*\s*(\w+)', text_upper)
            if match:
                return keyword, match.group(1)
            else:
                return keyword, "Tidak Terdefinisi"
                
    return None, None

def show_description(df: pd.DataFrame):
    st.header("📝 Analisis Kategori dan Solusi")

    if 'DESCRIPTION ACTUAL SOLUTION' not in df.columns:
        st.error("Kolom 'DESCRIPTION ACTUAL SOLUTION' tidak ditemukan dalam dataset.")
        return

    df_desc = df[['DESCRIPTION ACTUAL SOLUTION']].copy()
    df_desc[['KATEGORI', 'Solusi']] = df_desc['DESCRIPTION ACTUAL SOLUTION'].apply(
        lambda x: pd.Series(extract_solution_info(x))
    )
    df_desc.dropna(subset=['KATEGORI'], inplace=True)

    if df_desc.empty:
        st.warning("Tidak ditemukan kata kunci 'INDIHOME', 'GAMAS', atau 'SIP_TRUNK' dalam data solusi.")
        return

    st.sidebar.subheader("Opsi Tampilan Analisis")
    analysis_choice = st.sidebar.radio(
        "Pilih jenis analisis:",
        ("Analisis Umum", "Perbandingan Spesifik INDIHOME", "Perbandingan Spesifik GAMAS") # [DIUBAH] Menambahkan pilihan baru
    )

    if analysis_choice == "Analisis Umum":
        st.subheader("📊 Jumlah Insiden per Kategori")
        kategori_summary = df_desc['KATEGORI'].value_counts().reset_index()
        kategori_summary.columns = ['KATEGORI', 'JUMLAH']
        st.dataframe(kategori_summary)

        fig1 = px.bar(
            kategori_summary, 
            x='KATEGORI', 
            y='JUMLAH', 
            color='KATEGORI', 
            text='JUMLAH', 
            title="Jumlah Insiden per Kategori Utama",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig1.update_traces(textposition='outside')
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📊 Solusi Terpopuler berdasarkan Kategori")
        kata_kedua_summary = df_desc.groupby(['KATEGORI', 'Solusi']).size().reset_index(name='JUMLAH')
        
        st.subheader("📜 Tabel Rangkuman Solusi per Kategori")
        table_to_display = kata_kedua_summary.copy()
        table_to_display.columns = ['Kategori', 'Solusi', 'Jumlah']
        table_to_display = table_to_display[['Solusi', 'Kategori', 'Jumlah']]
        st.dataframe(table_to_display.sort_values(by='Jumlah', ascending=False).reset_index(drop=True))

        if not kata_kedua_summary.empty:
            max_items = len(kata_kedua_summary)
            
            top_n = st.slider(
                "Jumlah Solusi teratas yang ingin ditampilkan:",
                min_value=min(5, max_items),
                max_value=max_items,
                value=min(15, max_items)
            )
            
            kata_kedua_filtered = kata_kedua_summary.sort_values(by='JUMLAH', ascending=False).head(top_n)

            if not kata_kedua_filtered.empty:
                fig2 = px.bar(
                    kata_kedua_filtered,
                    x='JUMLAH',
                    y='Solusi',
                    color='KATEGORI',
                    orientation='h',
                    title=f"Top {top_n} Solusi Terpopuler",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig2.update_layout(
                    height=max(400, len(kata_kedua_filtered) * 25),
                    yaxis={'categoryorder':'total ascending'}
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Tidak ada data untuk ditampilkan.")

    elif analysis_choice == "Perbandingan Spesifik INDIHOME":
        st.subheader("⚖️ Peringkat Solusi Spesifik di Kategori INDIHOME")

        indihome_df = df_desc[df_desc['KATEGORI'] == 'INDIHOME'].copy()

        if indihome_df.empty:
            st.warning("Tidak ada data solusi yang terkategori sebagai INDIHOME.")
            return

        Solusi_counts = indihome_df['Solusi'].value_counts().reset_index()
        Solusi_counts.columns = ['Solusi', 'Jumlah']

        max_items = len(Solusi_counts)
        if max_items == 0:
            st.info("Tidak ada data Solusi untuk ditampilkan.")
            return

        top_n = st.slider(
            "Jumlah Solusi teratas yang ingin ditampilkan:",
            min_value=min(1, max_items),
            max_value=max_items,
            value=min(10, max_items),
            key="indihome_slider"
        )
        
        top_Solusi = Solusi_counts.head(top_n)

        st.dataframe(top_Solusi)

        fig_compare = px.bar(
            top_Solusi.sort_values(by='Jumlah', ascending=True),
            x='Jumlah',
            y='Solusi',
            orientation='h',
            text='Jumlah',
            title=f"Top {top_n} Solusi Terpopuler untuk INDIHOME",
            color='Solusi',
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        fig_compare.update_traces(textposition='outside')
        fig_compare.update_layout(
            yaxis_title="Solusi",
            xaxis_title="Jumlah Insiden",
            height=max(400, top_n * 30),
            showlegend=False
        )
        st.plotly_chart(fig_compare, use_container_width=True)

    # [BARU] Halaman analisis untuk GAMAS
    elif analysis_choice == "Perbandingan Spesifik GAMAS":
        st.subheader("Peringkat Solusi Spesifik di Kategori GAMAS")

        gamas_df = df_desc[df_desc['KATEGORI'] == 'GAMAS'].copy()

        if gamas_df.empty:
            st.warning("Tidak ada data solusi yang terkategori sebagai GAMAS.")
            return

        Solusi_counts = gamas_df['Solusi'].value_counts().reset_index()
        Solusi_counts.columns = ['Solusi', 'Jumlah']

        max_items = len(Solusi_counts)
        if max_items == 0:
            st.info("Tidak ada data Solusi untuk ditampilkan.")
            return

        top_n = st.slider(
            "Jumlah Solusi teratas yang ingin ditampilkan:",
            min_value=min(1, max_items),
            max_value=max_items,
            value=min(10, max_items),
            key="gamas_slider"
        )
        
        top_Solusi = Solusi_counts.head(top_n)

        st.dataframe(top_Solusi)

        fig_compare_gamas = px.bar(
            top_Solusi.sort_values(by='Jumlah', ascending=True),
            x='Jumlah',
            y='Solusi',
            orientation='h',
            text='Jumlah',
            title=f"Top {top_n} Solusi Terpopuler untuk GAMAS",
            color='Solusi',
            color_discrete_sequence=px.colors.qualitative.Plotly # Palet warna berbeda
        )
        fig_compare_gamas.update_traces(textposition='outside')
        fig_compare_gamas.update_layout(
            yaxis_title="Solusi",
            xaxis_title="Jumlah Insiden",
            height=max(400, top_n * 30),
            showlegend=False
        )
        st.plotly_chart(fig_compare_gamas, use_container_width=True)
