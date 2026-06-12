from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ASSET_KEYS = ("cash", "tesouro_selic", "tesouro_ipca", "fundos_rf", "renda_variavel")


def calibrate_parameters(
    macro_path: Path,
    equity_monthly_path: Path,
    tesouro_summary_path: Path,
    cvm_summary_path: Path,
    output_path: Path,
) -> dict[str, object]:
    macro_rows = read_csv(macro_path)
    equity_rows = read_csv(equity_monthly_path)
    tesouro_rows = read_csv(tesouro_summary_path)
    cvm_rows = read_csv(cvm_summary_path)

    selic_returns = [float(row["selic_return"]) for row in macro_rows]
    ipca_rates = [float(row["ipca_rate"]) for row in macro_rows]
    equity_returns = [float(row["equity_return"]) for row in equity_rows]
    cvm_summary = cvm_rows[0] if cvm_rows else {}

    equity_vol = stdev(equity_returns)
    selic_vol = stdev(selic_returns)
    ipca_vol = stdev(ipca_rates)
    cvm_flow_ratio = safe_div(
        float(cvm_summary.get("saldo_captacao_resgate", 0.0)),
        float(cvm_summary.get("patrimonio_liquido", 0.0)),
    )

    tesouro_rates = {
        row["tipo_titulo"]: {
            "taxa_compra_media": float(row["taxa_compra_media"]),
            "taxa_venda_media": float(row["taxa_venda_media"]),
            "titulos_ofertados": int(float(row["titulos_ofertados"])),
        }
        for row in tesouro_rows
    }

    calibration = {
        "fontes": {
            "macro": str(macro_path),
            "renda_variavel": str(equity_monthly_path),
            "tesouro": str(tesouro_summary_path),
            "cvm": str(cvm_summary_path),
        },
        "metricas_observadas": {
            "vol_mensal_selic": selic_vol,
            "vol_mensal_ipca": ipca_vol,
            "vol_mensal_renda_variavel": equity_vol,
            "saldo_fluxo_cvm_sobre_pl": cvm_flow_ratio,
        },
        "risco_sugerido": {
            "cash": 0.01,
            "tesouro_selic": max(0.02, selic_vol * 8),
            "tesouro_ipca": max(0.05, ipca_vol * 8),
            "fundos_rf": max(0.04, abs(cvm_flow_ratio) * 20),
            "renda_variavel": max(0.12, equity_vol * 5),
        },
        "parametros_comportamentais": {
            "crowding_penalty_base": 0.02,
            "crowding_penalty_sugerido": 0.02 + min(0.03, abs(cvm_flow_ratio) * 10),
            "imitation_stress_multiplier_base": 8,
            "imitation_bias_observacao": "Ajustar empiricamente quando houver experimento de manada com dados de fluxo.",
        },
        "tesouro_taxas_mais_recentes": tesouro_rates,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(calibration, indent=2, ensure_ascii=False), encoding="utf-8")
    return calibration


def load_simulation_calibration(path: Path) -> dict[str, object]:
    calibration = json.loads(path.read_text(encoding="utf-8"))
    risk_values = calibration.get("risco_sugerido", {})
    behavioral = calibration.get("parametros_comportamentais", {})

    return {
        "source": str(path),
        "asset_risk": {
            asset: float(risk_values[asset])
            for asset in ASSET_KEYS
            if asset in risk_values
        },
        "crowding_penalty": float(behavioral.get("crowding_penalty_sugerido", 0.02)),
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def stdev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    avg = sum(values) / len(values)
    return math.sqrt(sum((value - avg) ** 2 for value in values) / (len(values) - 1))


def safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
