import streamlit as st
import pandas as pd

def show_pratinjau(df: pd.DataFrame):
    st.subheader("📄 Pratinjau Data Mentah Insiden")

    st.write(f"Jumlah Baris: **{df.shape[0]}**")
    st.write(f"Jumlah Kolom: **{df.shape[1]}**")

    st.dataframe(df.head(100))

    st.subheader("📌 Informasi Kolom Dataset")
    st.write("Berikut adalah daftar kolom dan tipe datanya:")
    cols_df = pd.DataFrame({
        "Nama Kolom": df.columns,
        "Tipe Data": df.dtypes.astype(str)
    })
    st.dataframe(cols_df)
