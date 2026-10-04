import math

import streamlit as st

from src.preprocessing import load_processed_dataset
from src.utils import format_rupiah, option_with_all

st.set_page_config(page_title="Dataset - TourismRank", page_icon="TR", layout="wide")

df = load_processed_dataset()

st.title("Dataset")
st.caption("Data destinasi wisata setelah tahap cleaning, parsing harga, dan encoding popularitas.")

col1, col2, col3 = st.columns([2, 1, 1])
search = col1.text_input("Search", placeholder="Cari nama destinasi atau deskripsi")
province = col2.selectbox("Provinsi", option_with_all(df["province"]))
tourism_type = col3.selectbox("Jenis wisata", option_with_all(df["type"]))

filtered = df.copy()
if search:
    query = search.lower()
    filtered = filtered[
        filtered["destination"].str.lower().str.contains(query, na=False)
        | filtered["description"].str.lower().str.contains(query, na=False)
    ]
if province != "Semua":
    filtered = filtered[filtered["province"] == province]
if tourism_type != "Semua":
    filtered = filtered[filtered["type"] == tourism_type]

page_size = st.selectbox("Jumlah data per halaman", [10, 25, 50, 100], index=0)
total_pages = max(1, math.ceil(len(filtered) / page_size))
page = st.number_input("Halaman", min_value=1, max_value=total_pages, value=1)
start = (page - 1) * page_size
end = start + page_size

display = filtered.iloc[start:end].copy()
display["Harga"] = display["ticket_price"].map(format_rupiah)
display = display.rename(
    columns={
        "destination": "Nama",
        "province": "Provinsi",
        "type": "Jenis",
        "popularity": "Popularitas",
        "best_time": "Waktu terbaik",
    }
)

st.write(f"Menampilkan {len(display)} dari {len(filtered)} data.")
st.dataframe(
    display[["Nama", "Provinsi", "Jenis", "Harga", "Popularitas", "Waktu terbaik"]],
    use_container_width=True,
    hide_index=True,
)
