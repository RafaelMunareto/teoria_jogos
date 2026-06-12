from __future__ import annotations

import csv
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.request import Request, urlopen

from teoria_jogos.data.bcb import read_macro_csv, write_macro_csv


B3_COTAHIST_URL = "https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP"


@dataclass(frozen=True)
class EquityObservation:
    date: date
    symbol: str
    close: float


def download_cotahist_year(year: int, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_path = raw_dir / f"COTAHIST_A{year}.ZIP"
    url = B3_COTAHIST_URL.format(year=year)
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urlopen(request, timeout=60) as response, output_path.open("wb") as file:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            file.write(chunk)

    return output_path


def parse_cotahist_symbol(zip_path: Path, symbol: str) -> list[EquityObservation]:
    observations: list[EquityObservation] = []
    normalized_symbol = symbol.upper().strip()

    with zipfile.ZipFile(zip_path) as archive:
        data_file = next(name for name in archive.namelist() if name.upper().endswith(".TXT"))
        with archive.open(data_file) as raw_file:
            for raw_line in raw_file:
                line = raw_line.decode("latin-1")
                if line[:2] != "01":
                    continue
                if line[12:24].strip() != normalized_symbol:
                    continue
                observations.append(
                    EquityObservation(
                        date=datetime.strptime(line[2:10], "%Y%m%d").date(),
                        symbol=normalized_symbol,
                        close=int(line[108:121]) / 100,
                    )
                )

    return observations


def write_equity_daily_csv(path: Path, observations: list[EquityObservation]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    previous_close: float | None = None
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["date", "symbol", "close", "return"])
        writer.writeheader()
        for observation in sorted(observations, key=lambda item: item.date):
            daily_return = 0.0
            if previous_close and previous_close > 0:
                daily_return = (observation.close / previous_close) - 1
            previous_close = observation.close
            writer.writerow(
                {
                    "date": observation.date.isoformat(),
                    "symbol": observation.symbol,
                    "close": observation.close,
                    "return": daily_return,
                }
            )


def build_monthly_equity_returns(observations: list[EquityObservation]) -> list[dict[str, float | str]]:
    last_by_month: dict[tuple[int, int], EquityObservation] = {}
    for observation in sorted(observations, key=lambda item: item.date):
        last_by_month[(observation.date.year, observation.date.month)] = observation

    records: list[dict[str, float | str]] = []
    previous_close: float | None = None
    for year, month in sorted(last_by_month):
        observation = last_by_month[(year, month)]
        monthly_return = 0.0
        if previous_close and previous_close > 0:
            monthly_return = (observation.close / previous_close) - 1
        previous_close = observation.close
        records.append(
            {
                "month": f"{year:04d}-{month:02d}-01",
                "symbol": observation.symbol,
                "close": observation.close,
                "equity_return": monthly_return,
                "equity_return_source": f"b3_cotahist_{observation.symbol.lower()}",
            }
        )
    return records


def write_monthly_equity_csv(path: Path, records: list[dict[str, float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["month", "symbol", "close", "equity_return", "equity_return_source"],
        )
        writer.writeheader()
        writer.writerows(records)


def read_monthly_equity_csv(path: Path) -> dict[str, dict[str, float | str]]:
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return {
            row["month"]: {
                "equity_return": float(row["equity_return"]),
                "equity_return_source": row["equity_return_source"],
            }
            for row in reader
        }


def enrich_macro_with_equity(
    macro_path: Path,
    equity_monthly_path: Path,
    output_path: Path,
) -> list[dict[str, float | str]]:
    macro_records = read_macro_csv(macro_path)
    equity_by_month = read_monthly_equity_csv(equity_monthly_path)

    enriched_records: list[dict[str, float | str]] = []
    for record in macro_records:
        enriched = dict(record)
        equity_record = equity_by_month.get(str(record["month"]))
        if equity_record:
            enriched["equity_return"] = equity_record["equity_return"]
            enriched["equity_return_source"] = equity_record["equity_return_source"]
        enriched_records.append(enriched)

    write_macro_csv(output_path, enriched_records)
    return enriched_records


def build_b3_equity_dataset(
    year: int,
    symbol: str,
    raw_dir: Path,
    daily_output: Path,
    monthly_output: Path,
) -> list[dict[str, float | str]]:
    zip_path = download_cotahist_year(year, raw_dir)
    observations = parse_cotahist_symbol(zip_path, symbol)
    if not observations:
        raise ValueError(f"Nenhuma observacao encontrada para {symbol} em {zip_path}.")

    write_equity_daily_csv(daily_output, observations)
    monthly_records = build_monthly_equity_returns(observations)
    write_monthly_equity_csv(monthly_output, monthly_records)
    return monthly_records
