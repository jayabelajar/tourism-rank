from __future__ import annotations

import pandas as pd

from .preprocessing import score_time, score_type
from .utils import CRITERIA, normalize_weights


def build_decision_matrix(
    df: pd.DataFrame,
    preferred_type: str | None = None,
    travel_month: str | int | None = None,
) -> pd.DataFrame:
    matrix = df.copy()
    matrix["type_score"] = matrix["type"].map(lambda value: score_type(value, preferred_type))
    matrix["time_score"] = matrix["best_time"].map(lambda value: score_time(value, travel_month))
    return matrix


def normalize_matrix(matrix: pd.DataFrame) -> pd.DataFrame:
    normalized = matrix.copy()
    max_price = float(normalized["ticket_price"].max()) if not normalized.empty else 0
    if max_price <= 0 or normalized["ticket_price"].nunique(dropna=False) <= 1:
        normalized["norm_price"] = 1.0
    else:
        normalized["norm_price"] = 1 - (normalized["ticket_price"] / max_price)

    benefit_pairs = [
        ("popularity_score", "norm_popularity"),
        ("type_score", "norm_type"),
        ("time_score", "norm_time"),
    ]
    for source, target in benefit_pairs:
        max_value = float(normalized[source].max()) if not normalized.empty else 0
        normalized[target] = 1.0 if max_value <= 0 else normalized[source] / max_value
    return normalized


def calculate_preference(normalized: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    result = normalized.copy()
    normalized_weights = normalize_weights(weights)
    result["contribution_price"] = result["norm_price"] * normalized_weights["price"]
    result["contribution_popularity"] = result["norm_popularity"] * normalized_weights["popularity"]
    result["contribution_type"] = result["norm_type"] * normalized_weights["type"]
    result["contribution_time"] = result["norm_time"] * normalized_weights["time"]
    result["saw_score"] = (
        result["contribution_price"]
        + result["contribution_popularity"]
        + result["contribution_type"]
        + result["contribution_time"]
    ).clip(0, 1)
    return result


def calculate_ranking(
    df: pd.DataFrame,
    preferred_type: str | None,
    travel_month: str | int | None,
    weights: dict[str, float],
    province: str | None = None,
) -> dict[str, pd.DataFrame]:
    alternatives = df.copy()
    if province and province != "Semua":
        alternatives = alternatives[alternatives["province"] == province].copy()

    decision = build_decision_matrix(alternatives, preferred_type, travel_month)
    normalized = normalize_matrix(decision)
    preference = calculate_preference(normalized, weights)
    ranking = preference.sort_values("saw_score", ascending=False).reset_index(drop=True)
    ranking["rank"] = ranking.index + 1

    criteria_columns = ["destination"] + [criterion["column"] for criterion in CRITERIA]
    normalized_columns = ["destination"] + [criterion["normalized_column"] for criterion in CRITERIA]
    preference_columns = [
        "rank",
        "destination",
        "province",
        "type",
        "ticket_price",
        "popularity",
        "best_time",
        "saw_score",
        "contribution_price",
        "contribution_popularity",
        "contribution_type",
        "contribution_time",
    ]
    return {
        "alternatives": alternatives.reset_index(drop=True),
        "decision_matrix": decision[criteria_columns].reset_index(drop=True),
        "normalized_matrix": normalized[normalized_columns].reset_index(drop=True),
        "preference": preference.reset_index(drop=True),
        "ranking": ranking[preference_columns].reset_index(drop=True),
    }
