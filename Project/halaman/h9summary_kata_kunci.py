import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
import re

def show_summary_kata_kunci(df: pd.DataFrame):
    st.header("🧠 Analisis Topik Masalah dari Ringkasan Laporan (SUMMARY)")

    if 'SUMMARY' not in df.columns:
        st.warning("Kolom 'SUMMARY' tidak ditemukan dalam dataset.")
        return

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
    text_summary = re.sub(r'[^a-z\s]', '', text_summary)  # hapus karakter non-huruf
    all_words = text_summary.split()

    # --- Whitelist Kata Kunci ---
    whitelist_keywords = [kw.strip() for kw in keyword_list_input.lower().split(',') if kw.strip()]
    if not whitelist_keywords:
        st.warning("Mohon masukkan minimal satu kata kunci yang valid.")
        return

    filtered = [word for word in all_words if word in whitelist_keywords]
    word_counts = Counter(filtered)
    selected_words = [(w, c) for w, c in word_counts.items() if c >= min_freq]
    selected_words = sorted(selected_words, key=lambda x: x[1], reverse=True)[:max_words]

    if not selected_words:
        st.info("Tidak ada kata dari whitelist yang ditemukan dalam data.")
        return

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
