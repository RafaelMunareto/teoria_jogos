from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from teoria_jogos.analysis.reports import generate_analysis_outputs
from teoria_jogos.data.b3 import build_b3_equity_dataset_range, build_monthly_equity_returns, parse_cotahist_symbol
from teoria_jogos.data.cvm import summarize_cvm_inf_diario
from teoria_jogos.data.tesouro import summarize_tesouro_rates
from teoria_jogos.models.calibration import calibrate_parameters, load_simulation_calibration


class DataSourcesTest(unittest.TestCase):
    def test_parse_cotahist_symbol_and_monthly_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "cotahist.zip"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr(
                    "COTAHIST_A2024.TXT",
                    "\n".join(
                        [
                            cotahist_line("20240131", "BOVA11", 10000),
                            cotahist_line("20240229", "BOVA11", 11000),
                            cotahist_line("20240229", "ABCD3", 5000),
                        ]
                    ),
                )

            observations = parse_cotahist_symbol(zip_path, "BOVA11")
            monthly = build_monthly_equity_returns(observations)

            self.assertEqual(len(observations), 2)
            self.assertEqual(monthly[1]["month"], "2024-02-01")
            self.assertAlmostEqual(float(monthly[1]["equity_return"]), 0.1)

    def test_build_b3_equity_dataset_range_merges_years(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for year, date_value, close in [
                (2024, "20241230", 10000),
                (2025, "20250131", 10500),
            ]:
                with zipfile.ZipFile(root / f"COTAHIST_A{year}.ZIP", "w") as archive:
                    archive.writestr(f"COTAHIST_A{year}.TXT", cotahist_line(date_value, "BOVA11", close))

            def fake_download(year: int, raw_dir: Path) -> Path:
                return root / f"COTAHIST_A{year}.ZIP"

            with patch("teoria_jogos.data.b3.download_cotahist_year", side_effect=fake_download):
                records = build_b3_equity_dataset_range(
                    start_year=2024,
                    end_year=2025,
                    symbol="BOVA11",
                    raw_dir=root,
                    daily_output=root / "daily.csv",
                    monthly_output=root / "monthly.csv",
                )

            self.assertEqual(len(records), 2)
            self.assertAlmostEqual(float(records[1]["equity_return"]), 0.05)
            self.assertTrue((root / "daily.csv").exists())
            self.assertTrue((root / "monthly.csv").exists())

    def test_summarize_tesouro_rates_latest_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            raw_path = Path(tmp) / "tesouro.csv"
            output_path = Path(tmp) / "summary.csv"
            raw_path.write_text(
                "\n".join(
                    [
                        "Tipo Titulo;Data Vencimento;Data Base;Taxa Compra Manha;Taxa Venda Manha;PU Compra Manha;PU Venda Manha;PU Base Manha",
                        "Tesouro Selic;01/03/2027;01/01/2024;10,00;10,10;100,00;99,00;98,00",
                        "Tesouro Selic;01/03/2029;02/01/2024;11,00;11,10;101,00;100,00;99,00",
                        "Tesouro IPCA+;15/05/2035;02/01/2024;6,00;6,10;102,00;101,00;100,00",
                    ]
                ),
                encoding="latin-1",
            )

            records = summarize_tesouro_rates(raw_path, output_path)

            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["data_base"], "2024-01-02")

    def test_summarize_cvm_inf_diario_latest_date(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "cvm.zip"
            output_path = Path(tmp) / "summary.csv"
            with zipfile.ZipFile(zip_path, "w") as archive:
                archive.writestr(
                    "inf_diario_fi_202401.csv",
                    "\n".join(
                        [
                            "TP_FUNDO_CLASSE;CNPJ_FUNDO_CLASSE;ID_SUBCLASSE;DT_COMPTC;VL_TOTAL;VL_QUOTA;VL_PATRIM_LIQ;CAPTC_DIA;RESG_DIA;NR_COTST",
                            "CLASSES - FIF;00.1;;2024-01-01;100.00;1.0;90.00;5.00;2.00;10",
                            "CLASSES - FIF;00.2;;2024-01-02;200.00;1.0;180.00;7.00;3.00;20",
                        ]
                    ),
                )

            summary = summarize_cvm_inf_diario(zip_path, output_path)

            self.assertEqual(summary["data_competencia"], "2024-01-02")
            self.assertEqual(summary["fundos"], 1)
            self.assertEqual(summary["cotistas"], 20)

    def test_generate_analysis_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "baseline.json"
            scenarios = root / "scenarios.csv"
            shocks = root / "shocks.csv"
            rebalances = root / "rebalances.csv"
            profiles = root / "profiles.csv"
            output_dir = root / "report"
            hypotheses = root / "avaliacao.md"
            final_report = root / "relatorio_final.md"

            baseline.write_text(json.dumps(summary_row("none")), encoding="utf-8")
            scenarios.write_text(
                "scenario,cumulative_return,max_drawdown,final_hhi_concentration,final_weight_tesouro_selic,final_weight_renda_variavel\n"
                "imitation_0,0.10,-0.01,0.20,0.20,0.25\n"
                "imitation_2,0.09,-0.02,0.19,0.22,0.20\n",
                encoding="utf-8",
            )
            shocks.write_text(
                "scenario,cumulative_return,max_drawdown,final_hhi_concentration,final_weight_tesouro_selic,final_weight_renda_variavel\n"
                "none,0.10,-0.01,0.20,0.20,0.25\n"
                "rate_hike,0.08,-0.02,0.21,0.30,0.15\n"
                "equity_stress,0.04,-0.06,0.25,0.35,0.05\n"
                "combined_stress,0.03,-0.07,0.26,0.40,0.03\n",
                encoding="utf-8",
            )
            rebalances.write_text(
                "scenario,cumulative_return,max_drawdown,final_hhi_concentration,final_weight_tesouro_selic,final_weight_renda_variavel\n"
                "slow_clean,0.10,-0.01,0.20,0.20,0.25\n"
                "fast_noisy,0.08,-0.03,0.22,0.25,0.15\n",
                encoding="utf-8",
            )
            profiles.write_text(
                "scenario,cumulative_return,max_drawdown,final_hhi_concentration,final_weight_tesouro_selic,final_weight_renda_variavel\n"
                "heterogeneous,0.10,-0.01,0.20,0.20,0.25\n"
                "homogeneous_agressivo,0.07,-0.05,0.25,0.10,0.60\n",
                encoding="utf-8",
            )

            generate_analysis_outputs(baseline, scenarios, shocks, rebalances, profiles, output_dir, hypotheses, final_report)

            self.assertTrue((output_dir / "final_metrics.csv").exists())
            self.assertTrue((output_dir / "shock_returns.svg").exists())
            self.assertIn("H1", hypotheses.read_text(encoding="utf-8"))
            self.assertIn("Relatorio Final", final_report.read_text(encoding="utf-8"))

    def test_calibrate_parameters_outputs_risk_estimates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            macro = root / "macro.csv"
            equity = root / "equity.csv"
            tesouro = root / "tesouro.csv"
            cvm = root / "cvm.csv"
            output = root / "calibration.json"

            macro.write_text(
                "month,selic_return,ipca_rate,usd_brl,usd_return,equity_return,equity_return_source\n"
                "2024-01-01,0.008,0.004,5.0,0.0,0.02,b3\n"
                "2024-02-01,0.007,0.003,5.1,0.02,-0.01,b3\n",
                encoding="utf-8",
            )
            equity.write_text(
                "month,symbol,close,equity_return,equity_return_source\n"
                "2024-01-01,BOVA11,100.0,0.02,b3\n"
                "2024-02-01,BOVA11,99.0,-0.01,b3\n",
                encoding="utf-8",
            )
            tesouro.write_text(
                "data_base,tipo_titulo,titulos_ofertados,taxa_compra_media,taxa_venda_media,pu_base_medio,vencimento_min,vencimento_max\n"
                "2024-01-02,Tesouro Selic,1,0.03,0.04,100.0,2027-01-01,2027-01-01\n",
                encoding="utf-8",
            )
            cvm.write_text(
                "data_competencia,fundos,vl_total,patrimonio_liquido,captacao_dia,resgate_dia,saldo_captacao_resgate,cotistas\n"
                "2024-01-02,1,1000.0,900.0,20.0,10.0,10.0,100\n",
                encoding="utf-8",
            )

            calibration = calibrate_parameters(macro, equity, tesouro, cvm, output)
            loaded = load_simulation_calibration(output)

            self.assertTrue(output.exists())
            self.assertIn("renda_variavel", calibration["risco_sugerido"])
            self.assertIn("renda_variavel", loaded["asset_risk"])
            self.assertIn("crowding_penalty", loaded)


def cotahist_line(date: str, symbol: str, close_cents: int) -> str:
    line = list(" " * 245)
    line[0:2] = "01"
    line[2:10] = date
    line[12:24] = f"{symbol:<12}"
    line[108:121] = f"{close_cents:013d}"
    return "".join(line)


def summary_row(scenario: str) -> dict[str, float | str]:
    return {
        "scenario": scenario,
        "cumulative_return": 0.1,
        "max_drawdown": -0.01,
        "final_hhi_concentration": 0.2,
        "final_weight_tesouro_selic": 0.2,
        "final_weight_renda_variavel": 0.25,
    }


if __name__ == "__main__":
    unittest.main()
