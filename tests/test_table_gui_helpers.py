# -*- coding: utf-8 -*-
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from gui.tables.table_gui import build_initial_row


class TestTableGuiHelpers(unittest.TestCase):
    def test_build_initial_row_empty_data(self):
        columns = ["kv", "lines_count"]
        self.assertEqual(build_initial_row(columns, {}), ["-", "-"])
        self.assertEqual(build_initial_row(columns, None), ["-", "-"])

    def test_build_initial_row_maps_by_column_names(self):
        columns = ["kv", "lines_count", "extra"]
        data = {"kv": 50, "lines_count": 2}
        self.assertEqual(build_initial_row(columns, data), [50, 2, "-"])


if __name__ == "__main__":
    unittest.main()
