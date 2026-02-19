# -*- coding: utf-8 -*-
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from core.DataModel import Data_model


class TestPressureParsing(unittest.TestCase):
    def setUp(self):
        # _calculate_pressure_range does not depend on storage/DB managers
        self.model = Data_model(None, None, None, None)

    def test_calculate_pressure_range_without_colon_keys(self):
        pressure = {
            "Минимальное давление": 1.0,
            "Максимальное давление": 1.4,
            "Шаг значения": 0.2,
        }
        result = self.model._calculate_pressure_range(pressure)
        self.assertEqual(result, [1.0, 1.2, 1.4])

    def test_calculate_pressure_range_with_colon_keys(self):
        pressure = {
            "Минимальное давление:": 1.0,
            "Максимальное давление:": 1.4,
            "Шаг значения:": 0.2,
        }
        result = self.model._calculate_pressure_range(pressure)
        self.assertEqual(result, [1.0, 1.2, 1.4])


if __name__ == "__main__":
    unittest.main()
