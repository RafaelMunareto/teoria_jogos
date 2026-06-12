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
from urllib.request import urlopen


BCB_API_BASE_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados"

BCB_SERIES = {
    "selic": 11,
    "ipca": 433,
    "usd_brl": 1,
}


@dataclass(frozen=True)
class SgsObservation:
    date: date
    value: float


def fetch_sgs_series(series_id: int, start_date: str, end_date: str) -> list[SgsObservation]:
    params = urlencode(
        {
            "formato": "json",
            "dataInicial": start_date,
            "dataFinal": end_date,
        }
    )
    url = f"{BCB_API_BASE_URL.format(series_id=series_id)}?{params}"

    with urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

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
) -> list[dict[str, float | str]]:
    selic_by_month = _group_by_month(selic)
    ipca_by_month = _group_by_month(ipca)
    usd_by_month = _group_by_month(usd_brl)

    months = sorted(set(selic_by_month) & set(ipca_by_month))
    previous_usd_quote: float | None = None
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

        records.append(
            {
                "month": f"{month[0]:04d}-{month[1]:02d}-01",
                "selic_return": selic_return,
                "ipca_rate": ipca_rate,
                "usd_brl": usd_quote,
                "usd_return": usd_return,
            }
        )

    return records


def write_macro_csv(path: Path, records: Iterable[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["month", "selic_return", "ipca_rate", "usd_brl", "usd_return"]
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
                }
            )
        return records


def download_bcb_macro_dataset(
    start_date: str,
    end_date: str,
    raw_dir: Path,
    processed_path: Path,
) -> list[dict[str, float | str]]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    downloaded: dict[str, list[SgsObservation]] = {}

    for name, series_id in BCB_SERIES.items():
        observations = fetch_sgs_series(series_id, start_date, end_date)
        downloaded[name] = observations
        write_observations_csv(raw_dir / f"bcb_sgs_{name}.csv", observations)

    records = build_macro_dataset(
        selic=downloaded["selic"],
        ipca=downloaded["ipca"],
        usd_brl=downloaded["usd_brl"],
    )
    write_macro_csv(processed_path, records)
    return records


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
