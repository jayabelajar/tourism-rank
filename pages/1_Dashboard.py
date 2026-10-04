import plotly.express as px
import streamlit as st

from src.preprocessing import load_processed_dataset
from src.utils import format_rupiah

st.set_page_config(page_title="Dashboard - TourismRank", page_icon="TR", layout="wide")

df = load_processed_dataset()

st.title("Dashboard")
st.caption("Ringkasan dataset destinasi wisata yang digunakan dalam SPK SAW.")

total_destinations = len(df)
total_provinces = df["province"].nunique()
total_types = df["type"].nunique()
average_price = df["ticket_price"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Destinasi", f"{total_destinations:,}".replace(",", "."))
col2.metric("Total Provinsi", total_provinces)
col3.metric("Kategori Wisata", total_types)
col4.metric("Rata-rata Harga", format_rupiah(average_price))

left, right = st.columns(2)
with left:
    type_counts = df["type"].value_counts().reset_index()
    type_counts.columns = ["Jenis wisata", "Jumlah"]
    st.plotly_chart(
        px.bar(type_counts, x="Jenis wisata", y="Jumlah", title="Distribusi Kategori Wisata"),
        use_container_width=True,
    )

with right:
    popularity_counts = df["popularity"].value_counts().reset_index()
    popularity_counts.columns = ["Popularitas", "Jumlah"]
    st.plotly_chart(
        px.pie(popularity_counts, names="Popularitas", values="Jumlah", title="Distribusi Popularitas"),
        use_container_width=True,
    )

st.subheader("Statistik Harga Tiket")
price_col1, price_col2, price_col3, price_col4 = st.columns(4)
price_col1.metric("Minimum", format_rupiah(df["ticket_price"].min()))
price_col2.metric("Median", format_rupiah(df["ticket_price"].median()))
price_col3.metric("Maksimum", format_rupiah(df["ticket_price"].max()))
price_col4.metric("Gratis", int((df["ticket_price"] == 0).sum()))

st.plotly_chart(
    px.histogram(df, x="ticket_price", nbins=20, title="Sebaran Harga Tiket"),
    use_container_width=True,
)
