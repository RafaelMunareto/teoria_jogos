from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.request import urlopen


TESOURO_RATES_URL = (
    "https://www.tesourotransparente.gov.br/ckan/dataset/"
    "df56aa42-484a-4a59-8184-7676580c81e3/resource/"
    "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/precotaxatesourodireto.csv"
)


@dataclass
class TesouroRateAccumulator:
    count: int = 0
    buy_rate_sum: float = 0.0
    sell_rate_sum: float = 0.0
    base_price_sum: float = 0.0
    min_maturity: date | None = None
    max_maturity: date | None = None

    def add(self, row: dict[str, str]) -> None:
        maturity = parse_br_date(row["Data Vencimento"])
        self.count += 1
        self.buy_rate_sum += parse_br_decimal(row["Taxa Compra Manha"])
        self.sell_rate_sum += parse_br_decimal(row["Taxa Venda Manha"])
        self.base_price_sum += parse_br_decimal(row["PU Base Manha"])
        self.min_maturity = maturity if self.min_maturity is None else min(self.min_maturity, maturity)
        self.max_maturity = maturity if self.max_maturity is None else max(self.max_maturity, maturity)


def download_tesouro_rates(raw_path: Path) -> Path:
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(TESOURO_RATES_URL, timeout=60) as response, raw_path.open("wb") as file:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            file.write(chunk)
    return raw_path


def summarize_tesouro_rates(raw_path: Path, output_path: Path) -> list[dict[str, float | str]]:
    latest_date: date | None = None
    latest_rows: list[dict[str, str]] = []

    with raw_path.open("r", newline="", encoding="latin-1") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            base_date = parse_br_date(row["Data Base"])
            if latest_date is None or base_date > latest_date:
                latest_date = base_date
                latest_rows = [row]
            elif base_date == latest_date:
                latest_rows.append(row)

    grouped: dict[str, TesouroRateAccumulator] = defaultdict(TesouroRateAccumulator)
    for row in latest_rows:
        grouped[row["Tipo Titulo"]].add(row)

    records = []
    for title_type, accumulator in sorted(grouped.items()):
        records.append(
            {
                "data_base": latest_date.isoformat() if latest_date else "",
                "tipo_titulo": title_type,
                "titulos_ofertados": accumulator.count,
                "taxa_compra_media": accumulator.buy_rate_sum / accumulator.count,
                "taxa_venda_media": accumulator.sell_rate_sum / accumulator.count,
                "pu_base_medio": accumulator.base_price_sum / accumulator.count,
                "vencimento_min": accumulator.min_maturity.isoformat() if accumulator.min_maturity else "",
                "vencimento_max": accumulator.max_maturity.isoformat() if accumulator.max_maturity else "",
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0].keys()) if records else [])
        if records:
            writer.writeheader()
            writer.writerows(records)

    return records


def build_tesouro_summary(raw_path: Path, output_path: Path) -> list[dict[str, float | str]]:
    download_tesouro_rates(raw_path)
    return summarize_tesouro_rates(raw_path, output_path)


def parse_br_date(value: str) -> date:
    return datetime.strptime(value, "%d/%m/%Y").date()


def parse_br_decimal(value: str) -> float:
    if not value:
        return 0.0
    return float(value.replace(".", "").replace(",", "."))
