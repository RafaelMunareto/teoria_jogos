from __future__ import annotations

import unittest
from datetime import date

from teoria_jogos.data.bcb import SgsObservation, build_macro_dataset


class BcbDatasetTest(unittest.TestCase):
    def test_build_macro_dataset_compounds_selic_and_aligns_months(self) -> None:
        selic = [
            SgsObservation(date(2024, 1, 2), 0.05),
            SgsObservation(date(2024, 1, 3), 0.05),
            SgsObservation(date(2024, 2, 1), 0.04),
        ]
        ipca = [
            SgsObservation(date(2024, 1, 1), 0.42),
            SgsObservation(date(2024, 2, 1), 0.83),
        ]
        usd = [
            SgsObservation(date(2024, 1, 31), 5.0),
            SgsObservation(date(2024, 2, 29), 5.5),
        ]

        records = build_macro_dataset(selic, ipca, usd)

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["month"], "2024-01-01")
        self.assertEqual(round(float(records[0]["selic_return"]), 8), round((1.0005 * 1.0005) - 1, 8))
        self.assertEqual(records[0]["ipca_rate"], 0.0042)
        self.assertAlmostEqual(float(records[1]["usd_return"]), 0.1)


if __name__ == "__main__":
    unittest.main()
