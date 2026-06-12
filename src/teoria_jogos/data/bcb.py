from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.request import urlopen


BCB_API_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados"

BCB_SERIES = {
    "selic": 11,
    "ipca": 433,
    "usd_brl": 1,
}

BCB_OPTIONAL_SERIES = {
    "ibovespa": 7,
}


@dataclass(frozen=True)
class SgsObservation:
    date: date
    value: float


def fetch_sgs_series(
    series_id: int,
    start_date: str,
    end_date: str,
    allow_empty: bool = False,
) -> list[SgsObservation]:
    params = urlencode(
        {
            "formato": "json",
            "dataInicial": start_date,
            "dataFinal": end_date,
        }
    )
    url = f"{BCB_API_BASE_URL.format(series_id=series_id)}?{params}"

    try:
        with urlopen(url, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError:
        if allow_empty:
            return []
        raise

    if isinstance(payload, dict) and "erro" in payload:
        if allow_empty:
            return []
        raise ValueError(f"Serie SGS {series_id} indisponivel no periodo solicitado: {payload['erro']}")

    return [
        SgsObservation(
            date=datetime.strptime(item["data"], "%d/%m/%Y").date(),
            value=float(item["valor"].replace(",", ".")),
        )
        for item in payload
    ]


def write_observations_csv(path: Path, observations: Iterable[SgsObservation]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["date", "value"])
        writer.writeheader()
        for observation in observations:
            writer.writerow({"date": observation.date.isoformat(), "value": observation.value})


def read_observations_csv(path: Path) -> list[SgsObservation]:
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [
            SgsObservation(
                date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
                value=float(row["value"]),
            )
            for row in reader
        ]


def build_macro_dataset(
    selic: list[SgsObservation],
    ipca: list[SgsObservation],
    usd_brl: list[SgsObservation],
    ibovespa: list[SgsObservation] | None = None,
) -> list[dict[str, float | str]]:
    selic_by_month = _group_by_month(selic)
    ipca_by_month = _group_by_month(ipca)
    usd_by_month = _group_by_month(usd_brl)
    ibovespa_by_month = _group_by_month(ibovespa or [])

    months = sorted(set(selic_by_month) & set(ipca_by_month))
    previous_usd_quote: float | None = None
    previous_ibovespa_quote: float | None = None
    records: list[dict[str, float | str]] = []

    for month in months:
        selic_return = _compound_percent_values(observation.value for observation in selic_by_month[month])
        ipca_rate = ipca_by_month[month][-1].value / 100

        usd_quote = math.nan
        usd_return = 0.0
        if month in usd_by_month:
            usd_quote = usd_by_month[month][-1].value
            if previous_usd_quote and previous_usd_quote > 0:
                usd_return = (usd_quote / previous_usd_quote) - 1
            previous_usd_quote = usd_quote

        equity_return = math.nan
        equity_return_source = "synthetic_fallback"
        if month in ibovespa_by_month:
            ibovespa_quote = ibovespa_by_month[month][-1].value
            equity_return = 0.0
            if previous_ibovespa_quote and previous_ibovespa_quote > 0:
                equity_return = (ibovespa_quote / previous_ibovespa_quote) - 1
            previous_ibovespa_quote = ibovespa_quote
            equity_return_source = "ibovespa_sgs_7"

        records.append(
            {
                "month": f"{month[0]:04d}-{month[1]:02d}-01",
                "selic_return": selic_return,
                "ipca_rate": ipca_rate,
                "usd_brl": usd_quote,
                "usd_return": usd_return,
                "equity_return": equity_return,
                "equity_return_source": equity_return_source,
            }
        )

    return records


def write_macro_csv(path: Path, records: Iterable[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "month",
        "selic_return",
        "ipca_rate",
        "usd_brl",
        "usd_return",
        "equity_return",
        "equity_return_source",
    ]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def read_macro_csv(path: Path) -> list[dict[str, float | str]]:
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        records = []
        for row in reader:
            records.append(
                {
                    "month": row["month"],
                    "selic_return": float(row["selic_return"]),
                    "ipca_rate": float(row["ipca_rate"]),
                    "usd_brl": float(row["usd_brl"]),
                    "usd_return": float(row["usd_return"]),
                    "equity_return": _parse_optional_float(row.get("equity_return", "")),
                    "equity_return_source": row.get("equity_return_source", "synthetic_fallback"),
                }
            )
        return records


def download_bcb_macro_dataset(
    start_date: str,
    end_date: str,
    raw_dir: Path,
    processed_path: Path,
    include_ibovespa: bool = True,
) -> list[dict[str, float | str]]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    downloaded: dict[str, list[SgsObservation]] = {}

    for name, series_id in BCB_SERIES.items():
        observations = fetch_sgs_series(series_id, start_date, end_date)
        downloaded[name] = observations
        write_observations_csv(raw_dir / f"bcb_sgs_{name}.csv", observations)

    if include_ibovespa:
        ibovespa = fetch_sgs_series(
            BCB_OPTIONAL_SERIES["ibovespa"],
            start_date,
            end_date,
            allow_empty=True,
        )
        downloaded["ibovespa"] = ibovespa
        write_observations_csv(raw_dir / "bcb_sgs_ibovespa.csv", ibovespa)

    records = build_macro_dataset(
        selic=downloaded["selic"],
        ipca=downloaded["ipca"],
        usd_brl=downloaded["usd_brl"],
        ibovespa=downloaded.get("ibovespa"),
    )
    write_macro_csv(processed_path, records)
    return records


def _parse_optional_float(value: str) -> float:
    if not value:
        return math.nan
    try:
        return float(value)
    except ValueError:
        return math.nan


def _group_by_month(observations: Iterable[SgsObservation]) -> dict[tuple[int, int], list[SgsObservation]]:
    grouped: dict[tuple[int, int], list[SgsObservation]] = defaultdict(list)
    for observation in sorted(observations, key=lambda item: item.date):
        grouped[(observation.date.year, observation.date.month)].append(observation)
    return grouped


def _compound_percent_values(values: Iterable[float]) -> float:
    result = 1.0
    for value in values:
        result *= 1 + (value / 100)
    return result - 1
