import streamlit as st
import pandas as pd
import plotly.express as px

def show_service_type(df: pd.DataFrame):
    st.header("📡 Analisis Jenis Layanan Paling Sering Mengalami Gangguan")

    if 'SERVICE TYPE' in df.columns and 'INCIDENT' in df.columns:
        filtered_df = df[df['SERVICE TYPE'] != 'Tidak Diketahui']

        service_type_counts = (
            filtered_df.groupby('SERVICE TYPE')['INCIDENT']
            .count()
            .sort_values(ascending=False)
        )

        st.subheader("📋 Tabel Jumlah Gangguan per Jenis Layanan")
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

        # --- Diagram Batang Vertikal
        st.subheader("📊 Diagram Batang Vertikal")
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

        # --- Diagram Batang Horizontal
        st.subheader("📊 Diagram Batang Horizontal")
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

        # --- Facet Bar Chart jika ada kolom STATUS
        if 'STATUS' in df.columns:
            st.subheader("🧩 Diagram Bar Terpisah (Facet) Berdasarkan Status Tiket")
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
