# -*- coding: utf-8 -*-
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from core.calculate_Max_performance import Max_performance


class TestMaxPerformanceStability(unittest.TestCase):
    def setUp(self):
        self.calc = Max_performance()

    def test_find_nearest_pressure_data(self):
        data = [
            {"index": "Pout_0.2"},
            {"index": "Pout_0.5"},
            {"index": "Pout_0.8"},
        ]
        row = self.calc._find_nearest_pressure_data(data, 0.56)
        self.assertEqual(row["index"], "Pout_0.5")

    def test_interpolate_boiler_data(self):
        row = {
            "index": "Pout_0.4",
            "Pin_1_0": json.dumps({"Nm3h": 100.0, "C": 1}),
            "Pin_2_0": json.dumps({"Nm3h": 200.0, "C": 1}),
        }
        value = self.calc._interpolate_boiler_data(row, 1.5)
        self.assertAlmostEqual(value, 150.0, places=9)

    def test_interpolate_boiler_data_clamps_out_of_bounds(self):
        row = {
            "index": "Pout_0.4",
            "Pin_1_0": json.dumps({"Nm3h": 100.0, "C": 1}),
            "Pin_2_0": json.dumps({"Nm3h": 200.0, "C": 1}),
        }
        self.assertEqual(self.calc._interpolate_boiler_data(row, 0.7), 100.0)
        self.assertEqual(self.calc._interpolate_boiler_data(row, 2.5), 200.0)


if __name__ == "__main__":
    unittest.main()
