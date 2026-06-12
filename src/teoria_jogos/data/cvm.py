from __future__ import annotations

import csv
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from urllib.request import urlopen


CVM_INF_DIARIO_URL = "https://dados.cvm.gov.br/dados/FI/DOC/INF_DIARIO/DADOS/inf_diario_fi_{year_month}.zip"


@dataclass
class CvmFundAccumulator:
    fund_count: int = 0
    total_assets: float = 0.0
    net_worth: float = 0.0
    daily_inflows: float = 0.0
    daily_redemptions: float = 0.0
    holders: int = 0

    def add(self, row: dict[str, str]) -> None:
        self.fund_count += 1
        self.total_assets += parse_decimal(row["VL_TOTAL"])
        self.net_worth += parse_decimal(row["VL_PATRIM_LIQ"])
        self.daily_inflows += parse_decimal(row["CAPTC_DIA"])
        self.daily_redemptions += parse_decimal(row["RESG_DIA"])
        self.holders += int(float(row["NR_COTST"] or 0))


def download_cvm_inf_diario(year_month: str, raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_path = raw_dir / f"inf_diario_fi_{year_month}.zip"
    url = CVM_INF_DIARIO_URL.format(year_month=year_month)

    with urlopen(url, timeout=60) as response, output_path.open("wb") as file:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            file.write(chunk)

    return output_path


def summarize_cvm_inf_diario(zip_path: Path, output_path: Path) -> dict[str, float | str]:
    latest_date: date | None = None
    accumulator = CvmFundAccumulator()

    with zipfile.ZipFile(zip_path) as archive:
        csv_file = next(name for name in archive.namelist() if name.lower().endswith(".csv"))
        with archive.open(csv_file) as raw_file:
            text = (line.decode("latin-1") for line in raw_file)
            reader = csv.DictReader(text, delimiter=";")
            for row in reader:
                row_date = datetime.strptime(row["DT_COMPTC"], "%Y-%m-%d").date()
                if latest_date is None or row_date > latest_date:
                    latest_date = row_date
                    accumulator = CvmFundAccumulator()
                if row_date == latest_date:
                    accumulator.add(row)

    summary = {
        "data_competencia": latest_date.isoformat() if latest_date else "",
        "fundos": accumulator.fund_count,
        "vl_total": accumulator.total_assets,
        "patrimonio_liquido": accumulator.net_worth,
        "captacao_dia": accumulator.daily_inflows,
        "resgate_dia": accumulator.daily_redemptions,
        "saldo_captacao_resgate": accumulator.daily_inflows - accumulator.daily_redemptions,
        "cotistas": accumulator.holders,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)

    return summary


def build_cvm_summary(year_month: str, raw_dir: Path, output_path: Path) -> dict[str, float | str]:
    zip_path = download_cvm_inf_diario(year_month, raw_dir)
    return summarize_cvm_inf_diario(zip_path, output_path)


def parse_decimal(value: str) -> float:
    return float(value or 0)
