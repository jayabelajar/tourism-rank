import pandas as pd
import streamlit as st

from src.utils import CRITERIA, DEFAULT_WEIGHTS, validate_weights

st.set_page_config(page_title="Kriteria - TourismRank", page_icon="TR", layout="wide")

st.title("Kriteria")
st.caption("Kriteria yang digunakan dalam metode Simple Additive Weighting.")

criteria_df = pd.DataFrame(
    [
        {
            "Kode": item["code"],
            "Kriteria": item["name"],
            "Atribut Dataset": item["attribute"],
            "Jenis": item["type"],
            "Bobot Default": f"{item['default_weight']}%",
        }
        for item in CRITERIA
    ]
)
st.dataframe(criteria_df, use_container_width=True, hide_index=True)

st.subheader("Simulasi Bobot")
col1, col2, col3, col4 = st.columns(4)
weights = {
    "price": col1.number_input("Harga", min_value=0, max_value=100, value=DEFAULT_WEIGHTS["price"]),
    "popularity": col2.number_input("Popularitas", min_value=0, max_value=100, value=DEFAULT_WEIGHTS["popularity"]),
    "type": col3.number_input("Jenis wisata", min_value=0, max_value=100, value=DEFAULT_WEIGHTS["type"]),
    "time": col4.number_input("Waktu", min_value=0, max_value=100, value=DEFAULT_WEIGHTS["time"]),
}
total = sum(weights.values())
is_valid, message = validate_weights(weights)
st.metric("Total Bobot", f"{total}%")
if is_valid:
    st.success("Bobot valid.")
else:
    st.error(message)

st.markdown(
    """
    C1 menggunakan normalisasi cost `1 - (x / max(x))` agar destinasi gratis tetap aman dihitung.
    C2, C3, dan C4 menggunakan normalisasi benefit `x / max(x)`.
    """
)
