from __future__ import annotations

from calendar import month_name
from typing import Iterable


DEFAULT_WEIGHTS = {
    "price": 30,
    "popularity": 30,
    "type": 25,
    "time": 15,
}

CRITERIA = [
    {
        "code": "C1",
        "name": "Harga Tiket",
        "column": "ticket_price",
        "normalized_column": "norm_price",
        "weight_key": "price",
        "attribute": "ticket_range",
        "type": "Cost",
        "default_weight": DEFAULT_WEIGHTS["price"],
    },
    {
        "code": "C2",
        "name": "Popularitas",
        "column": "popularity_score",
        "normalized_column": "norm_popularity",
        "weight_key": "popularity",
        "attribute": "popularity",
        "type": "Benefit",
        "default_weight": DEFAULT_WEIGHTS["popularity"],
    },
    {
        "code": "C3",
        "name": "Kecocokan Jenis Wisata",
        "column": "type_score",
        "normalized_column": "norm_type",
        "weight_key": "type",
        "attribute": "type",
        "type": "Benefit",
        "default_weight": DEFAULT_WEIGHTS["type"],
    },
    {
        "code": "C4",
        "name": "Kecocokan Waktu",
        "column": "time_score",
        "normalized_column": "norm_time",
        "weight_key": "time",
        "attribute": "best_time",
        "type": "Benefit",
        "default_weight": DEFAULT_WEIGHTS["time"],
    },
]

MONTHS_ID = {
    "Januari": 1,
    "Februari": 2,
    "Maret": 3,
    "April": 4,
    "Mei": 5,
    "Juni": 6,
    "Juli": 7,
    "Agustus": 8,
    "September": 9,
    "Oktober": 10,
    "November": 11,
    "Desember": 12,
}

MONTH_ALIASES = {
    "jan": 1,
    "january": 1,
    "januari": 1,
    "feb": 2,
    "february": 2,
    "februari": 2,
    "mar": 3,
    "march": 3,
    "maret": 3,
    "apr": 4,
    "april": 4,
    "mei": 5,
    "may": 5,
    "jun": 6,
    "june": 6,
    "juni": 6,
    "jul": 7,
    "july": 7,
    "juli": 7,
    "aug": 8,
    "august": 8,
    "agustus": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "oktober": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
    "desember": 12,
}


def format_rupiah(value: float | int | None) -> str:
    if value is None:
        return "-"
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return "-"
    if amount <= 0:
        return "Gratis"
    return f"Rp{amount:,.0f}".replace(",", ".")


def validate_weights(weights: dict[str, float]) -> tuple[bool, str]:
    total = sum(float(value) for value in weights.values())
    if round(total, 6) != 100:
        return False, "Total bobot harus sama dengan 100%."
    if any(float(value) < 0 for value in weights.values()):
        return False, "Bobot tidak boleh bernilai negatif."
    return True, ""


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    return {key: float(value) / 100 for key, value in weights.items()}


def parse_month(value: str | int | float | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        month = int(value)
        return month if 1 <= month <= 12 else None
    text = str(value).strip().lower()
    return MONTH_ALIASES.get(text)


def months_in_range(start: int, end: int) -> set[int]:
    if start <= end:
        return set(range(start, end + 1))
    return set(range(start, 13)) | set(range(1, end + 1))


def month_label(month_number: int) -> str:
    for label, number in MONTHS_ID.items():
        if number == month_number:
            return label
    return month_name[month_number]


def option_with_all(values: Iterable[str]) -> list[str]:
    cleaned = sorted({str(value).strip() for value in values if str(value).strip()})
    return ["Semua"] + cleaned
