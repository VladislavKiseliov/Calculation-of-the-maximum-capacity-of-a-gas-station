import logging
import tkinter as tk
from tkinter import ttk
from core.table_domain import (
    BaseTableManager,
    RegulatorTableManager,
    BoilerTableManager,
    PipeTableManager,
    TableFactory,
)


class WidgetFactory:
    @staticmethod
    def create_entry(parent, row, column=1, padx=5, pady=5):
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=column, padx=padx, pady=pady)
        return entry

    @staticmethod
    def create_label(parent, label_text, row, column=0, padx=5, pady=5):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=column, padx=padx, pady=pady, sticky="w")
        return label

    @staticmethod
    def create_Button(parent, label_text, row, function=None, column=0, padx=5, pady=5):
        Button = ttk.Button(parent, text=label_text, command=function)
        Button.grid(row=row, column=column, padx=padx, pady=pady, sticky="ew")
        return Button


# Table domain classes are now defined in src/core/table_domain.py.
# They are imported here for backward compatibility with old imports/pickles.
