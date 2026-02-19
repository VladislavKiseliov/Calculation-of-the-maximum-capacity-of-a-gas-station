# -*- coding: utf-8 -*-
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.getcwd(), "src"))

from gui.controllers.table_controller import normalize_table_row


class TestTableControllerHelpers(unittest.TestCase):
    def test_normalize_table_row_none(self):
        self.assertEqual(normalize_table_row(None), {})

    def test_normalize_table_row_dict(self):
        payload = {"kv": 50, "lines_count": 1}
        self.assertEqual(normalize_table_row(payload), payload)

    def test_normalize_table_row_list_of_dict(self):
        payload = [{"kv": 40, "lines_count": 2}]
        self.assertEqual(normalize_table_row(payload), payload[0])

    def test_normalize_table_row_unexpected(self):
        self.assertEqual(normalize_table_row("bad"), {})


if __name__ == "__main__":
    unittest.main()
