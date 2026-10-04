from __future__ import annotations

from pathlib import Path

import pandas as pd

DATASET_NAME = "LorthGyu/indonesian-tourism"
RAW_PATH = Path("data/raw/indonesian_tourism.csv")
PROCESSED_PATH = Path("data/processed/tourism_saw.csv")

REQUIRED_COLUMNS = [
    "id",
    "destination",
    "province",
    "type",
    "description",
    "best_time",
    "ticket_range",
    "popularity",
]


def sample_dataset() -> pd.DataFrame:
    rows = [
        [1, "Pantai Kuta", "Bali", "Pantai", "Pantai ikonik dengan matahari terbenam dan aktivitas pesisir.", "April - Oktober", "Rp10.000", "sangat_populer"],
        [2, "Gunung Bromo", "Jawa Timur", "Alam", "Kawasan gunung berapi dengan pemandangan sunrise dan lautan pasir.", "Mei - September", "Rp29.000 - Rp34.000", "sangat_populer"],
        [3, "Candi Borobudur", "Jawa Tengah", "Budaya", "Candi Buddha bersejarah dengan relief dan panorama perbukitan.", "Mei - September", "Rp50.000", "sangat_populer"],
        [4, "Raja Ampat", "Papua Barat", "Bahari", "Kepulauan dengan terumbu karang dan kehidupan laut yang kaya.", "Oktober - April", "Rp100.000 - Rp250.000", "populer"],
        [5, "Taman Nasional Komodo", "Nusa Tenggara Timur", "Alam", "Habitat komodo dan lanskap savana pesisir.", "April - Desember", "Rp150.000", "sangat_populer"],
        [6, "Kawah Putih", "Jawa Barat", "Alam", "Danau kawah vulkanik dengan warna air yang khas.", "Juni - September", "Rp28.000", "populer"],
        [7, "Malioboro", "DI Yogyakarta", "Belanja", "Koridor wisata kota untuk kuliner, belanja, dan budaya jalanan.", "Sepanjang Tahun", "Gratis", "sangat_populer"],
        [8, "Danau Toba", "Sumatera Utara", "Alam", "Danau vulkanik besar dengan Pulau Samosir di tengahnya.", "Mei - September", "Rp5.000 - Rp15.000", "populer"],
        [9, "Tana Toraja", "Sulawesi Selatan", "Budaya", "Destinasi budaya dengan rumah adat dan tradisi pemakaman.", "Juni - Agustus", "Rp10.000 - Rp30.000", "populer"],
        [10, "Pulau Weh", "Aceh", "Bahari", "Pulau dengan spot snorkeling dan diving di ujung barat Indonesia.", "Maret - Oktober", "Rp5.000", "tersembunyi"],
        [11, "Museum Angkut", "Jawa Timur", "Edukasi", "Museum transportasi tematik dengan zona foto interaktif.", "Sepanjang Tahun", "Rp100.000", "populer"],
        [12, "Pantai Tanjung Tinggi", "Bangka Belitung", "Pantai", "Pantai berpasir putih dengan batu granit besar.", "April - Oktober", "Rp10.000", "populer"],
    ]
    return pd.DataFrame(rows, columns=REQUIRED_COLUMNS)


def ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "name": "destination",
        "place_name": "destination",
        "category": "type",
        "city": "province",
        "price": "ticket_range",
    }
    df = df.rename(columns={key: value for key, value in rename_map.items() if key in df.columns})
    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    return df[REQUIRED_COLUMNS].copy()


def load_raw_dataset(force_download: bool = False) -> pd.DataFrame:
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    if RAW_PATH.exists() and not force_download:
        return ensure_columns(pd.read_csv(RAW_PATH))

    try:
        from datasets import load_dataset

        dataset = load_dataset(DATASET_NAME)
        split_name = "train" if "train" in dataset else list(dataset.keys())[0]
        df = dataset[split_name].to_pandas()
        df = ensure_columns(df)
    except Exception:
        df = sample_dataset()

    df = remove_duplicates(df)
    df.to_csv(RAW_PATH, index=False)
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    if "id" not in df.columns:
        return df.drop_duplicates().reset_index(drop=True)
    return df.drop_duplicates(subset=["id"]).reset_index(drop=True)
