from __future__ import annotations

import random
import unittest

from teoria_jogos.simulation.baseline import (
    ASSETS,
    build_asset_returns,
    run_baseline_simulation,
    run_profile_comparison,
    run_rebalance_comparison,
    run_scenario_comparison,
    run_shock_comparison,
)


class BaselineSimulationTest(unittest.TestCase):
    def test_baseline_simulation_produces_history_and_normalized_weights(self) -> None:
        macro = [
            {
                "month": "2024-01-01",
                "selic_return": 0.008,
                "ipca_rate": 0.004,
                "usd_brl": 5.0,
                "usd_return": 0.0,
                "equity_return": 0.03,
            },
            {
                "month": "2024-02-01",
                "selic_return": 0.007,
                "ipca_rate": 0.003,
                "usd_brl": 5.1,
                "usd_return": 0.02,
                "equity_return": -0.02,
            },
        ]

        history, summary = run_baseline_simulation(
            macro,
            agent_count=9,
            seed=7,
            asset_risk={"renda_variavel": 0.35},
            crowding_penalty=0.03,
            calibration_source="test_calibration.json",
        )

        self.assertEqual(len(history), 2)
        self.assertEqual(summary["agent_count"], 9)
        self.assertEqual(summary["calibration_source"], "test_calibration.json")
        self.assertEqual(summary["asset_risk_renda_variavel"], 0.35)
        self.assertIn("risk_adjusted_return", summary)
        self.assertIn("avg_turnover", summary)
        final_weight_sum = sum(float(summary[f"final_weight_{asset}"]) for asset in ASSETS)
        self.assertEqual(round(final_weight_sum, 10), 1.0)
        self.assertGreater(float(summary["final_total_wealth"]), 0)

    def test_scenario_comparison_runs_multiple_imitation_levels(self) -> None:
        macro = [
            {
                "month": "2024-01-01",
                "selic_return": 0.008,
                "ipca_rate": 0.004,
                "usd_brl": 5.0,
                "usd_return": 0.0,
                "equity_return": 0.03,
            },
            {
                "month": "2024-02-01",
                "selic_return": 0.007,
                "ipca_rate": 0.003,
                "usd_brl": 5.1,
                "usd_return": 0.02,
                "equity_return": -0.02,
            },
        ]

        comparison = run_scenario_comparison(macro, imitation_levels=[0.0, 1.0, 2.0], agent_count=9, seed=7)

        self.assertEqual([row["scenario"] for row in comparison], ["imitation_0", "imitation_1", "imitation_2"])
        for row in comparison:
            final_weight_sum = sum(float(row[f"final_weight_{asset}"]) for asset in ASSETS)
            self.assertEqual(round(final_weight_sum, 10), 1.0)

    def test_asset_returns_use_real_equity_return_when_available(self) -> None:
        macro = [
            {
                "month": "2024-01-01",
                "selic_return": 0.008,
                "ipca_rate": 0.004,
                "usd_brl": 5.0,
                "usd_return": 0.0,
                "equity_return": 0.123,
            },
        ]

        asset_returns = build_asset_returns(macro, rng=random.Random(1))

        self.assertEqual(asset_returns[0]["renda_variavel"], 0.123)

    def test_shock_comparison_runs_macro_stress_scenarios(self) -> None:
        macro = [
            {
                "month": "2024-01-01",
                "selic_return": 0.008,
                "ipca_rate": 0.004,
                "usd_brl": 5.0,
                "usd_return": 0.0,
                "equity_return": 0.03,
            },
            {
                "month": "2024-02-01",
                "selic_return": 0.007,
                "ipca_rate": 0.003,
                "usd_brl": 5.1,
                "usd_return": 0.02,
                "equity_return": -0.02,
            },
            {
                "month": "2024-03-01",
                "selic_return": 0.007,
                "ipca_rate": 0.003,
                "usd_brl": 5.2,
                "usd_return": 0.02,
                "equity_return": 0.01,
            },
        ]

        comparison = run_shock_comparison(
            macro,
            shock_scenarios=["none", "rate_hike", "combined_stress"],
            agent_count=9,
            seed=7,
        )

        self.assertEqual([row["scenario"] for row in comparison], ["none", "rate_hike", "combined_stress"])
        self.assertEqual(comparison[2]["shock_scenario"], "combined_stress")

    def test_rebalance_and_profile_comparisons_run(self) -> None:
        macro = [
            {
                "month": "2024-01-01",
                "selic_return": 0.008,
                "ipca_rate": 0.004,
                "usd_brl": 5.0,
                "usd_return": 0.0,
                "equity_return": 0.03,
            },
            {
                "month": "2024-02-01",
                "selic_return": 0.007,
                "ipca_rate": 0.003,
                "usd_brl": 5.1,
                "usd_return": 0.02,
                "equity_return": -0.02,
            },
        ]

        rebalances = run_rebalance_comparison(macro, agent_count=9, seed=7)
        profiles = run_profile_comparison(macro, agent_count=9, seed=7)

        self.assertEqual(rebalances[0]["scenario"], "slow_clean")
        self.assertEqual(profiles[0]["scenario"], "heterogeneous")
        self.assertEqual(profiles[1]["profile_mode"], "homogeneous_conservador")


if __name__ == "__main__":
    unittest.main()
