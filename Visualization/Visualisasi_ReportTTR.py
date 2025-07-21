import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Dashboard Analisis Tiket", layout="wide")
st.title("📊 Dashboard Analisis Report TTR WSA")

# --- PEMUATAN DATA DI SIDEBAR ---
st.sidebar.title("Pengaturan Data")  # ⬅️ Taskbar samping (sidebar)

# PERBAIKAN: Mengizinkan unggahan file .csv dan .xlsx
uploaded_file = st.sidebar.file_uploader("Unggah file CSV atau XLSX Anda", type=['csv', 'xlsx'])  # ⬅️ Tempat unggah file

@st.cache_data  # Menggunakan cache untuk mempercepat pemuatan data
def load_data(uploaded_file):
    """Memuat data dari file yang diunggah dan melakukan pembersihan dasar."""
    try:
        # Memeriksa ekstensi file untuk menggunakan fungsi pembaca yang benar
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, engine='python', encoding='latin1', on_bad_lines='skip')
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Format file tidak didukung. Harap unggah file CSV atau XLSX.")
            return None

        # Mengisi nilai kosong di kolom object dengan 'Tidak Diketahui'
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].fillna('Tidak Diketahui')
        return df
    except Exception as e:
        st.error(f"Terjadi error saat memuat dan memproses data: {e}")
        return None

#  TAMPILAN UTAMA
# Aplikasi hanya akan berjalan jika file sudah diunggah
if uploaded_file is not None:
    df = load_data(uploaded_file)

    if df is not None:
        st.sidebar.title("Navigasi Analisis")  # ⬅️ Judul navigasi analisis di taskbar samping
        insight_options = [
            "Pratinjau Data Report TTR WSA",
            "Distribusi Tiket Berdasarkan Status",
            "Owner Group dengan Tiket Terbanyak"
        ]
        selected_insight = st.sidebar.selectbox("Pilih Analisis yang Ingin Dilihat", insight_options)  # ⬅️ Tempat pemilihan analisis

        # Halaman 1: Pratinjau Data Report TTR WSA
        if selected_insight == "Pratinjau Data Report TTR WSA":  # ⬅️ Halaman 1: Preview data
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
        elif selected_insight == "Distribusi Tiket Berdasarkan Status":  # ⬅️ Halaman 2: Distribusi berdasarkan status
            st.header("Analisis Distribusi Tiket Berdasarkan Status")
            
            if 'STATUS' in df.columns and 'INCIDENT' in df.columns:
                # Menghapus baris dengan status 'Tidak Diketahui'
                filtered_df = df[df['STATUS'] != 'Tidak Diketahui']

                # Hitung jumlah insiden (baris) per status berdasarkan kolom 'INCIDENT'
                status_counts = filtered_df.groupby('STATUS')['INCIDENT'].count().sort_values(ascending=False)
                
                st.subheader("Tabel Jumlah Tiket per Status")
                st.dataframe(status_counts)
                
                st.subheader("Diagram Batang (Bar Chart)")
                st.write("Visualisasi ini membandingkan jumlah tiket di setiap kategori status (tanpa 'Tidak Diketahui').")
                st.bar_chart(status_counts)
                
                st.subheader("Diagram Lingkaran (Pie Chart)")
                st.write("Visualisasi ini menunjukkan proporsi (persentase) setiap status terhadap keseluruhan tiket.")
                fig_pie, ax_pie = plt.subplots(figsize=(8, 6))
                ax_pie.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
                ax_pie.axis('equal')
                st.pyplot(fig_pie)

            else:
                st.warning("Kolom 'STATUS' atau 'INCIDENT' tidak ditemukan dalam dataset.")

        elif selected_insight == "Owner Group dengan Tiket Terbanyak":  # ⬅️ Halaman 3: Analisis owner group terbanyak
            st.header("Analisis Owner Group dengan Tiket Terbanyak")
            
            if 'OWNER GROUP' in df.columns and 'INCIDENT' in df.columns:
                # Hapus baris 'Tidak Diketahui' dari OWNER GROUP
                filtered_df = df[df['OWNER GROUP'] != 'Tidak Diketahui']

                unique_owner_groups = filtered_df['OWNER GROUP'].nunique()
                min_slider = min(5, unique_owner_groups)

                # Slider jumlah top N
                top_n = st.slider(
                    "Pilih jumlah Top 'Owner Group' yang ingin ditampilkan:",
                    min_value=min_slider,
                    max_value=unique_owner_groups,
                    value=min(10, unique_owner_groups)
                )

                # Hitung berdasarkan jumlah insiden (baris) per OWNER GROUP
                owner_group_counts = filtered_df.groupby('OWNER GROUP')['INCIDENT'].count().nlargest(top_n)

                st.subheader("Diagram Batang (Bar Chart)")
                st.write(f"Visualisasi ini mengurutkan {top_n} Owner Group yang paling banyak menangani tiket (tanpa 'Tidak Diketahui').")
                st.bar_chart(owner_group_counts)
                
                st.subheader("Diagram Batang Horizontal (Untuk Keterbacaan Lebih Baik)")
                st.write("Diagram batang horizontal seringkali lebih mudah dibaca ketika nama kategori panjang.")
                fig_bar, ax_bar = plt.subplots(figsize=(10, 8))
                sns.barplot(y=owner_group_counts.index, x=owner_group_counts.values, palette='plasma', ax=ax_bar)
                ax_bar.set_xlabel('Jumlah Tiket', fontsize=12)
                ax_bar.set_ylabel('Owner Group', fontsize=12)
                ax_bar.set_title(f'Top {top_n} Owner Group dengan Tiket Terbanyak', fontsize=15)
                for index, value in enumerate(owner_group_counts.values):
                    ax_bar.text(value, index, f' {value}', va='center')
                st.pyplot(fig_bar)

            else:
                st.warning("Kolom 'OWNER GROUP' atau 'INCIDENT' tidak ditemukan dalam dataset.")

else:
    st.info("Silakan unggah file CSV atau XLSX pada sidebar untuk memulai analisis.")
