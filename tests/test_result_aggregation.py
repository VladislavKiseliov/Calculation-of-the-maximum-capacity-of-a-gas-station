# -*- coding: utf-8 -*-
import unittest
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from core.application_service import (
    summarize_constraints,
    prepare_line_plot_data,
    prepare_limiting_map_data,
    build_final_results_long,
)


class TestResultAggregation(unittest.TestCase):
    def test_summarize_constraints_builds_expected_metrics(self):
        constraints = pd.DataFrame(
            {
                "Pin_1_0": [100.0, 90.0, 95.0],
                "Pin_1_5": [80.0, 85.0, 79.0],
                "Pin_2_0": [70.0, 72.0, 71.0],
            },
            index=["regulator_A", "pipe_B", "boiler_C"],
        )

        q_final, limiting_table, margin_to_next = summarize_constraints(constraints)

        self.assertEqual(q_final["Pin_1_0"], 90.0)
        self.assertEqual(q_final["Pin_1_5"], 79.0)
        self.assertEqual(q_final["Pin_2_0"], 70.0)

        self.assertEqual(limiting_table["Pin_1_0"], "pipe_B")
        self.assertEqual(limiting_table["Pin_1_5"], "boiler_C")
        self.assertEqual(limiting_table["Pin_2_0"], "regulator_A")

        self.assertAlmostEqual(margin_to_next["Pin_1_0"], 5.0, places=9)
        self.assertAlmostEqual(margin_to_next["Pin_1_5"], 1.0, places=9)
        self.assertAlmostEqual(margin_to_next["Pin_2_0"], 1.0, places=9)

    def test_summarize_constraints_handles_single_constraint(self):
        constraints = pd.DataFrame(
            {"Pin_1_0": [100.0], "Pin_1_5": [80.0]},
            index=["only_table"],
        )

        q_final, limiting_table, margin_to_next = summarize_constraints(constraints)

        self.assertEqual(q_final["Pin_1_0"], 100.0)
        self.assertEqual(limiting_table["Pin_1_5"], "only_table")
        self.assertTrue(pd.isna(margin_to_next["Pin_1_0"]))

    def test_summarize_constraints_rejects_empty_dataframe(self):
        with self.assertRaises(ValueError):
            summarize_constraints(pd.DataFrame())

    def test_prepare_line_plot_data_sorts_pin_columns(self):
        df_result = pd.DataFrame(
            [{"Pin_2_0": 200.0, "Pin_1_0": 100.0, "Pin_1_5": 150.0}],
            index=[0.4],
        )

        sorted_columns, labels, out_values, series_map = prepare_line_plot_data(df_result)

        self.assertEqual(sorted_columns, ["Pin_1_0", "Pin_1_5", "Pin_2_0"])
        self.assertEqual(labels, ["1.0", "1.5", "2.0"])
        self.assertEqual(out_values, [0.4])
        self.assertEqual(series_map[0.4].tolist(), [100.0, 150.0, 200.0])

    def test_prepare_limiting_map_data_builds_code_matrix(self):
        df_limiting = pd.DataFrame(
            [
                {"Pin_2_0": "pipe_B", "Pin_1_0": "reg_A"},
                {"Pin_2_0": "boiler_C", "Pin_1_0": "reg_A"},
            ],
            index=[0.3, 0.4],
        )

        pin_labels, out_values, table_names, code_matrix = prepare_limiting_map_data(df_limiting)

        self.assertEqual(pin_labels, ["1.0", "2.0"])
        self.assertEqual(out_values, [0.3, 0.4])
        self.assertEqual(table_names, ["boiler_C", "pipe_B", "reg_A"])
        self.assertEqual(code_matrix.shape, (2, 2))

    def test_build_final_results_long_creates_expected_rows(self):
        df_result = pd.DataFrame(
            [
                {"Pin_1_0": 100.0, "Pin_1_5": 95.0},
                {"Pin_1_0": 90.0, "Pin_1_5": 88.0},
            ],
            index=[0.3, 0.4],
        )
        df_limiting = pd.DataFrame(
            [
                {"Pin_1_0": "reg_A", "Pin_1_5": "pipe_B"},
                {"Pin_1_0": "boiler_C", "Pin_1_5": "pipe_B"},
            ],
            index=[0.3, 0.4],
        )
        df_margin = pd.DataFrame(
            [
                {"Pin_1_0": 5.0, "Pin_1_5": 3.0},
                {"Pin_1_0": 2.0, "Pin_1_5": 1.0},
            ],
            index=[0.3, 0.4],
        )

        df_long = build_final_results_long(df_result, df_limiting, df_margin)

        self.assertEqual(len(df_long), 4)
        self.assertEqual(
            set(df_long.columns),
            {"P_out", "Pin", "Q_final", "limiting_table", "margin_to_next"},
        )

        row = df_long[(df_long["P_out"] == 0.4) & (df_long["Pin"] == "1.5")].iloc[0]
        self.assertEqual(row["Q_final"], 88.0)
        self.assertEqual(row["limiting_table"], "pipe_B")
        self.assertEqual(row["margin_to_next"], 1.0)


if __name__ == "__main__":
    unittest.main()
