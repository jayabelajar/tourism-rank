import streamlit as st

from src.preprocessing import load_processed_dataset
from src.saw import calculate_ranking
from src.utils import DEFAULT_WEIGHTS, MONTHS_ID, format_rupiah, option_with_all, validate_weights

st.set_page_config(page_title="Hasil Ranking - TourismRank", page_icon="TR", layout="wide")

df = load_processed_dataset()

st.title("Hasil Ranking")
st.caption("Rekomendasi destinasi berdasarkan nilai preferensi SAW terbesar.")

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

valid, message = validate_weights(weights)
if not valid:
    st.error(message)
    st.stop()

result = calculate_ranking(df, preferred_type, travel_month, weights, province)
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

if ranking.empty:
    st.warning("Tidak ada destinasi untuk kombinasi filter ini.")
    st.stop()

st.subheader("Detail Destinasi")
selected = st.selectbox("Pilih destinasi", ranking["destination"].tolist())
detail = ranking[ranking["destination"] == selected].iloc[0]
source_detail = df[df["destination"] == selected].iloc[0]

left, right = st.columns([2, 1])
with left:
    st.markdown(f"### {detail['destination']}")
    st.write(source_detail["description"])
    st.write(f"Provinsi: {detail['province']}")
    st.write(f"Jenis wisata: {detail['type']}")
    st.write(f"Harga tiket: {format_rupiah(detail['ticket_price'])}")
    st.write(f"Popularitas: {detail['popularity']}")
    st.write(f"Waktu terbaik: {detail['best_time']}")

with right:
    st.metric("Ranking", int(detail["rank"]))
    st.metric("Score SAW", f"{detail['saw_score']:.4f}")

contributions = {
    "Harga": detail["contribution_price"],
    "Popularitas": detail["contribution_popularity"],
    "Jenis": detail["contribution_type"],
    "Waktu": detail["contribution_time"],
}
st.subheader("Kontribusi Kriteria")
st.dataframe(
    {
        "Kriteria": list(contributions.keys()) + ["Total"],
        "Kontribusi": [round(value, 4) for value in contributions.values()] + [round(detail["saw_score"], 4)],
    },
    use_container_width=True,
    hide_index=True,
)
