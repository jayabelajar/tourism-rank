import streamlit as st

from src.custom_dataset import render_dataset_source
from src.saw import calculate_ranking
from src.utils import DEFAULT_WEIGHTS, MONTHS_ID, format_rupiah, option_with_all, validate_weights

st.set_page_config(page_title="Perhitungan SAW - TourismRank", page_icon="TR", layout="wide")

df, dataset_name = render_dataset_source("calculation")

st.title("Perhitungan SAW")
st.caption(f"Dataset aktif: {dataset_name}. Masukkan preferensi untuk melihat proses perhitungan.")

with st.sidebar:
    st.header("Preferensi")
    province = st.selectbox("Provinsi", option_with_all(df["province"]))
    preferred_type = st.selectbox("Jenis wisata", option_with_all(df["type"]), index=1 if df["type"].nunique() else 0)
    travel_month = st.selectbox("Bulan perjalanan", list(MONTHS_ID.keys()), index=6)
    st.header("Bobot")
    weights = {
        "price": st.number_input("Harga", min_value=0, max_value=100, value=DEFAULT_WEIGHTS["price"]),
        "popularity": st.number_input("Popularitas", min_value=0, max_value=100, value=DEFAULT_WEIGHTS["popularity"]),
        "type": st.number_input("Jenis wisata", min_value=0, max_value=100, value=DEFAULT_WEIGHTS["type"]),
        "time": st.number_input("Waktu", min_value=0, max_value=100, value=DEFAULT_WEIGHTS["time"]),
    }
    calculate = st.button("Hitung Ranking", type="primary", use_container_width=True)

valid, message = validate_weights(weights)
if not valid:
    st.error(message)
    st.stop()

if not calculate and "saw_result" not in st.session_state:
    st.info("Klik Hitung Ranking untuk memulai proses SAW.")
    st.stop()

params = {
    "dataset_name": dataset_name,
    "province": province,
    "preferred_type": preferred_type,
    "travel_month": travel_month,
    "weights": weights,
}

if calculate or st.session_state.get("saw_params") != params:
    st.session_state["saw_result"] = calculate_ranking(df, preferred_type, travel_month, weights, province)
    st.session_state["saw_params"] = params

result = st.session_state["saw_result"]

st.subheader("Step 1 - Data Alternatif")
alternatives = result["alternatives"].copy()
alternatives["Harga"] = alternatives["ticket_price"].map(format_rupiah)
st.dataframe(
    alternatives[["destination", "province", "type", "Harga", "popularity", "best_time"]].rename(
        columns={
            "destination": "Destinasi",
            "province": "Provinsi",
            "type": "Jenis",
            "popularity": "Popularitas",
            "best_time": "Waktu terbaik",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Step 2 - Matriks Keputusan")
st.dataframe(result["decision_matrix"], use_container_width=True, hide_index=True)

st.subheader("Step 3 - Normalisasi Matriks")
st.dataframe(result["normalized_matrix"].round(4), use_container_width=True, hide_index=True)

st.subheader("Step 4 - Bobot Kriteria")
st.dataframe(
    {
        "Kriteria": ["Harga", "Popularitas", "Jenis wisata", "Waktu"],
        "Bobot (%)": [weights["price"], weights["popularity"], weights["type"], weights["time"]],
        "Bobot Desimal": [weights["price"] / 100, weights["popularity"] / 100, weights["type"] / 100, weights["time"] / 100],
    },
    use_container_width=True,
    hide_index=True,
)

st.subheader("Step 5 - Nilai Preferensi")
preference = result["preference"].copy()
st.dataframe(
    preference[
        [
            "destination",
            "contribution_price",
            "contribution_popularity",
            "contribution_type",
            "contribution_time",
            "saw_score",
        ]
    ].round(4),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Step 6 - Ranking")
ranking = result["ranking"].copy()
ranking["Harga"] = ranking["ticket_price"].map(format_rupiah)
ranking["Nilai SAW"] = ranking["saw_score"].round(4)
st.dataframe(
    ranking[["rank", "destination", "province", "type", "Harga", "popularity", "Nilai SAW"]].rename(
        columns={
            "rank": "Rank",
            "destination": "Nama Destinasi",
            "province": "Provinsi",
            "type": "Jenis",
            "popularity": "Popularitas",
        }
    ),
    use_container_width=True,
    hide_index=True,
)
