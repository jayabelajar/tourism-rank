from __future__ import annotations

from io import BytesIO
from typing import Iterable

import pandas as pd
import streamlit as st

from .dataset import REQUIRED_COLUMNS, load_raw_dataset
from .preprocessing import preprocess_dataset

COLUMN_ALIASES = {
    "id": ["id", "no", "kode", "code"],
    "destination": ["destination", "destinasi", "nama", "name", "place_name", "tempat", "wisata"],
    "province": ["province", "provinsi", "city", "kota", "location", "lokasi"],
    "type": ["type", "jenis", "kategori", "category", "tipe"],
    "description": ["description", "deskripsi", "desc", "keterangan"],
    "best_time": ["best_time", "waktu_terbaik", "musim", "bulan", "best time"],
    "ticket_range": ["ticket_range", "harga", "price", "ticket", "tiket", "biaya"],
    "popularity": ["popularity", "popularitas", "rating", "score", "nilai"],
}


def _normalize_name(value: object) -> str:
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


def _guess_column(columns: Iterable[str], target: str) -> str | None:
    normalized = {_normalize_name(column): column for column in columns}
    for alias in COLUMN_ALIASES[target]:
        key = _normalize_name(alias)
        if key in normalized:
            return normalized[key]
    for column in columns:
        key = _normalize_name(column)
        if any(_normalize_name(alias) in key for alias in COLUMN_ALIASES[target]):
            return column
    return None


def read_uploaded_csv(uploaded_file) -> pd.DataFrame:
    content = uploaded_file.getvalue()
    for encoding in ["utf-8", "utf-8-sig", "latin1"]:
        try:
            return pd.read_csv(BytesIO(content), encoding=encoding, sep=None, engine="python")
        except UnicodeDecodeError:
            continue
    return pd.read_csv(BytesIO(content), sep=None, engine="python")


def map_uploaded_dataset(source: pd.DataFrame, mapping: dict[str, str | None]) -> pd.DataFrame:
    mapped = pd.DataFrame()
    for column in REQUIRED_COLUMNS:
        source_column = mapping.get(column)
        if source_column and source_column in source.columns:
            mapped[column] = source[source_column]
        elif column == "id":
            mapped[column] = range(1, len(source) + 1)
        else:
            mapped[column] = ""
    return mapped[REQUIRED_COLUMNS]


def render_dataset_source(prefix: str) -> tuple[pd.DataFrame, str]:
    key_prefix = "active"
    source_type = st.sidebar.radio(
        "Sumber dataset",
        ["Dataset bawaan", "Upload CSV"],
        key=f"{key_prefix}_dataset_source",
    )

    if source_type == "Dataset bawaan":
        raw = load_raw_dataset(force_download=False)
        return preprocess_dataset(raw), "Dataset bawaan"

    uploaded_file = st.sidebar.file_uploader(
        "Upload dataset CSV",
        type=["csv"],
        key=f"{key_prefix}_dataset_upload",
    )
    if uploaded_file is None:
        st.sidebar.info("Upload CSV untuk memakai dataset sendiri. Sementara aplikasi menampilkan dataset bawaan.")
        raw = load_raw_dataset(force_download=False)
        return preprocess_dataset(raw), "Dataset bawaan"

    try:
        uploaded_df = read_uploaded_csv(uploaded_file)
    except Exception as exc:
        st.sidebar.error(f"CSV gagal dibaca: {exc}")
        raw = load_raw_dataset(force_download=False)
        return preprocess_dataset(raw), "Dataset bawaan"

    if uploaded_df.empty:
        st.sidebar.warning("CSV kosong. Aplikasi menampilkan dataset bawaan.")
        raw = load_raw_dataset(force_download=False)
        return preprocess_dataset(raw), "Dataset bawaan"

    options = [""] + list(uploaded_df.columns)
    mapping: dict[str, str | None] = {}
    with st.sidebar.expander("Mapping kolom CSV", expanded=True):
        labels = {
            "id": "ID",
            "destination": "Nama destinasi",
            "province": "Provinsi/lokasi",
            "type": "Jenis/kategori",
            "description": "Deskripsi",
            "best_time": "Waktu terbaik",
            "ticket_range": "Harga tiket",
            "popularity": "Popularitas/rating",
        }
        for column in REQUIRED_COLUMNS:
            guess = _guess_column(uploaded_df.columns, column)
            default_index = options.index(guess) if guess in options else 0
            selected = st.selectbox(
                labels[column],
                options,
                index=default_index,
                key=f"{key_prefix}_map_{column}",
            )
            mapping[column] = selected or None

    required_mapping = ["destination", "province", "type", "ticket_range", "popularity"]
    missing = [item for item in required_mapping if not mapping.get(item)]
    if missing:
        st.sidebar.warning("Lengkapi mapping kolom utama agar ranking lebih akurat.")

    raw = map_uploaded_dataset(uploaded_df, mapping)
    processed = preprocess_dataset(raw)
    st.sidebar.success(f"Dataset upload aktif: {len(processed)} baris.")
    return processed, uploaded_file.name
