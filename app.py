import streamlit as st

from src.custom_dataset import render_dataset_source
from src.dataset import load_raw_dataset
from src.preprocessing import load_processed_dataset

st.set_page_config(page_title="TourismRank", page_icon="TR", layout="wide")

df, dataset_name = render_dataset_source("home")

st.title("TourismRank")
st.caption("Sistem Pendukung Keputusan perangkingan destinasi wisata Indonesia menggunakan metode SAW.")

st.markdown(
    """
    Buka halaman di sidebar untuk melihat dashboard, dataset, kriteria, proses perhitungan,
    dan hasil ranking. Gunakan panel sidebar untuk memilih dataset bawaan atau upload CSV sendiri.
    """
)

st.metric("Dataset aktif", dataset_name)
st.write(f"Total data siap diproses: {len(df)} baris.")

col1, col2 = st.columns(2)
with col1:
    if st.button("Siapkan Dataset", use_container_width=True):
        raw = load_raw_dataset(force_download=False)
        processed = load_processed_dataset(refresh=True)
        st.success(f"Dataset siap: {len(raw)} data mentah, {len(processed)} data preprocessing.")
with col2:
    if st.button("Refresh dari Hugging Face", use_container_width=True):
        raw = load_raw_dataset(force_download=True)
        processed = load_processed_dataset(refresh=True)
        st.success(f"Dataset diperbarui: {len(raw)} data mentah, {len(processed)} data preprocessing.")

st.info("Mulai dari halaman Dashboard atau Perhitungan SAW untuk menjalankan rekomendasi.")
