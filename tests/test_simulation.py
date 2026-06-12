from __future__ import annotations

import unittest

from teoria_jogos.simulation.baseline import ASSETS, run_baseline_simulation


class BaselineSimulationTest(unittest.TestCase):
    def test_baseline_simulation_produces_history_and_normalized_weights(self) -> None:
        macro = [
            {
                "month": "2024-01-01",
                "selic_return": 0.008,
                "ipca_rate": 0.004,
                "usd_brl": 5.0,
                "usd_return": 0.0,
            },
            {
                "month": "2024-02-01",
                "selic_return": 0.007,
                "ipca_rate": 0.003,
                "usd_brl": 5.1,
                "usd_return": 0.02,
            },
        ]

        history, summary = run_baseline_simulation(macro, agent_count=9, seed=7)

        self.assertEqual(len(history), 2)
        self.assertEqual(summary["agent_count"], 9)
        final_weight_sum = sum(float(summary[f"final_weight_{asset}"]) for asset in ASSETS)
        self.assertEqual(round(final_weight_sum, 10), 1.0)
        self.assertGreater(float(summary["final_total_wealth"]), 0)


if __name__ == "__main__":
    unittest.main()
