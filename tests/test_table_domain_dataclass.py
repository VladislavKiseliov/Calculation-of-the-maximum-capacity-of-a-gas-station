# -*- coding: utf-8 -*-
import os
import sys
import unittest
from dataclasses import is_dataclass

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from core.table_domain import (
    BaseTableManager,
    RegulatorTableManager,
    BoilerTableManager,
    PipeTableManager,
    TableFactory,
)


class TestTableDomainDataclass(unittest.TestCase):
    def test_table_managers_are_dataclasses(self):
        self.assertTrue(is_dataclass(RegulatorTableManager))
        self.assertTrue(is_dataclass(BoilerTableManager))
        self.assertTrue(is_dataclass(PipeTableManager))

    def test_columns_and_type_contract(self):
        mgr = RegulatorTableManager("Таблица для регуляторов")
        self.assertEqual(mgr.get_table_type(), "Таблица для регуляторов")
        self.assertEqual(mgr.get_columns(), ["kv", "lines_count"])

    def test_factory_returns_base_manager_instances(self):
        mgr = TableFactory.create_table_manager("Таблица котельной")
        self.assertIsInstance(mgr, BaseTableManager)
        self.assertEqual(mgr.get_columns(), ["boiler_power", "gas_temp_in", "gas_temp_out"])


if __name__ == "__main__":
    unittest.main()
