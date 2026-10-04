import streamlit as st

from src.dataset import load_raw_dataset
from src.preprocessing import load_processed_dataset

st.set_page_config(page_title="TourismRank", page_icon="TR", layout="wide")

st.title("TourismRank")
st.caption("Sistem Pendukung Keputusan perangkingan destinasi wisata Indonesia menggunakan metode SAW.")

st.markdown(
    """
    Buka halaman di sidebar untuk melihat dashboard, dataset, kriteria, proses perhitungan,
    dan hasil ranking. Data akan dibaca dari `data/raw/indonesian_tourism.csv`; jika belum ada,
    aplikasi mencoba mengambil dataset Hugging Face dan memakai data sampel bila koneksi belum siap.
    """
)

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
