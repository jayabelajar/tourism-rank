from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from .dataset import PROCESSED_PATH, load_raw_dataset, remove_duplicates
from .utils import MONTH_ALIASES, months_in_range, parse_month

POPULARITY_MAP = {
    "tersembunyi": 1,
    "hidden": 1,
    "rendah": 1,
    "kurang_populer": 1,
    "kurang populer": 1,
    "populer": 3,
    "popular": 3,
    "sedang": 3,
    "sangat_populer": 5,
    "sangat populer": 5,
    "very popular": 5,
    "tinggi": 5,
}

CATEGORY_GROUPS = {
    "alam": {"alam", "gunung", "danau", "air terjun", "hutan", "taman nasional", "agrowisata"},
    "pantai": {"pantai", "bahari", "laut", "pulau", "diving", "snorkeling"},
    "bahari": {"bahari", "pantai", "laut", "pulau", "diving", "snorkeling"},
    "budaya": {"budaya", "sejarah", "candi", "heritage", "museum", "religi"},
    "edukasi": {"edukasi", "museum", "sejarah", "budaya"},
    "belanja": {"belanja", "kuliner", "kota", "pasar"},
    "kuliner": {"kuliner", "belanja", "kota", "pasar"},
}


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def parse_ticket_price(value: object) -> float:
    text = clean_text(value).lower()
    if not text or "gratis" in text or text == "0":
        return 0.0
    numbers = [int(match.replace(".", "").replace(",", "")) for match in re.findall(r"\d[\d.,]*", text)]
    if not numbers:
        return 0.0
    if len(numbers) == 1:
        return float(numbers[0])
    return float(sum(numbers[:2]) / 2)


def encode_popularity(value: object) -> int:
    text = clean_text(value).lower().replace("-", "_")
    if text in POPULARITY_MAP:
        return POPULARITY_MAP[text]
    if any(word in text for word in ["sangat", "very", "high", "tinggi"]):
        return 5
    if any(word in text for word in ["populer", "popular", "sedang", "medium"]):
        return 3
    return 1


def parse_best_time(value: object) -> set[int]:
    text = clean_text(value).lower()
    if not text or "sepanjang" in text or "all year" in text:
        return set(range(1, 13))
    found = []
    for token, month in MONTH_ALIASES.items():
        for match in re.finditer(rf"\b{re.escape(token)}\b", text):
            found.append((match.start(), month))
    ordered_months = [month for _, month in sorted(found, key=lambda item: item[0])]
    deduped = list(dict.fromkeys(ordered_months))
    if len(deduped) >= 2 and re.search(r"(-|sampai|hingga|to)", text):
        return months_in_range(deduped[0], deduped[1])
    return set(deduped)


def score_type(destination_type: object, preferred_type: str | None) -> int:
    if not preferred_type or preferred_type == "Semua":
        return 5
    actual = clean_text(destination_type).lower()
    preferred = clean_text(preferred_type).lower()
    if not actual:
        return 1
    if preferred in actual or actual in preferred:
        return 5
    actual_tokens = {token.strip() for token in re.split(r"[,/&|-]", actual) if token.strip()}
    preferred_group = CATEGORY_GROUPS.get(preferred, {preferred})
    related = set()
    for token in actual_tokens | {actual}:
        related |= CATEGORY_GROUPS.get(token, {token})
    return 3 if related & preferred_group else 1


def score_time(best_time: object, travel_month: str | int | None) -> int:
    selected_month = parse_month(travel_month)
    if selected_month is None:
        return 5
    months = parse_best_time(best_time)
    if not months:
        return 3
    if selected_month in months:
        return 5
    near_months = {((selected_month - 2) % 12) + 1, (selected_month % 12) + 1}
    return 3 if months & near_months else 1


def preprocess_dataset(df: pd.DataFrame | None = None) -> pd.DataFrame:
    if df is None:
        df = load_raw_dataset()
    df = remove_duplicates(df).copy()

    text_columns = ["destination", "province", "type", "description", "best_time", "ticket_range", "popularity"]
    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].map(clean_text)

    df["ticket_price"] = df["ticket_range"].map(parse_ticket_price)
    df["popularity_score"] = df["popularity"].map(encode_popularity)
    df["best_time_months"] = df["best_time"].map(lambda value: ",".join(map(str, sorted(parse_best_time(value)))))

    required = ["ticket_price", "popularity_score"]
    df[required] = df[required].replace([np.inf, -np.inf], np.nan).fillna(0)
    return df.reset_index(drop=True)


def load_processed_dataset(refresh: bool = False) -> pd.DataFrame:
    path = Path(PROCESSED_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not refresh:
        return pd.read_csv(path)
    df = preprocess_dataset()
    df.to_csv(path, index=False)
    return df
