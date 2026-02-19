# -*- coding: utf-8 -*-
import os
import sys
import unittest
from dataclasses import is_dataclass

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from core.DataModel import Data_model, DataStorage, ModelSnapshot
from core.table_domain import RegulatorTableManager


class _StubCSV:
    pass


class _StubJSON:
    pass


class _StubDB:
    def load_data(self, table_name):
        if table_name == "Regulator_Main":
            return {"kv": 120.0, "lines_count": 2}
        return {}

    def get_data_table(self, table_name):
        if table_name == "Boiler_data":
            return [{"index": "Pout_0.2", "Pin_1_0": '{"Nm3h": 100, "C": 1}'}]
        return []


class TestModelSnapshot(unittest.TestCase):
    def setUp(self):
        storage = DataStorage()
        storage.data_gas_composition = {"Метан: CH4": 95.0, "Этан: C2H6": 5.0}
        storage.set_pressure_range("input", [1.0, 1.2, 1.4])
        storage.set_pressure_range("output", [0.2, 0.4])
        storage.temperature = {"input": 10.0, "output": 5.0}
        storage.table_manager = {
            "Regulator_Main": RegulatorTableManager("Таблица для регуляторов")
        }
        self.model = Data_model(storage, _StubCSV(), _StubDB(), _StubJSON())

    def test_get_snapshot_returns_dataclass(self):
        snapshot = self.model.get_snapshot()
        self.assertTrue(is_dataclass(snapshot))
        self.assertIsInstance(snapshot, ModelSnapshot)
        self.assertIn("Regulator_Main", snapshot.table_specs)
        self.assertIn("Regulator_Main", snapshot.table_parameters)
        self.assertEqual(snapshot.table_parameters["Regulator_Main"]["kv"], 120.0)
        self.assertEqual(len(snapshot.boiler_data), 1)

    def test_get_all_data_returns_plain_dict(self):
        payload = self.model.get_all_data()
        self.assertIsInstance(payload, dict)
        self.assertIn("gas_composition", payload)
        self.assertIn("table_specs", payload)
        self.assertIn("table_parameters", payload)


if __name__ == "__main__":
    unittest.main()
