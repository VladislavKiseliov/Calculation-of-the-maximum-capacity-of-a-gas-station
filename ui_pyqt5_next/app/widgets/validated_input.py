from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QLineEdit


class ValidatedNumberInput(QLineEdit):
    validity_changed = pyqtSignal(bool)

    def __init__(self, minimum: float = 0.0, maximum: float = 1_000_000.0, parent=None):
        super().__init__(parent)
        self.minimum = minimum
        self.maximum = maximum
        self.setValidator(QDoubleValidator(bottom=-1_000_000_000.0, top=1_000_000_000.0, decimals=6))
        self.textChanged.connect(self._validate)
        self._validate("")

    def value_or_none(self):
        text = self.text().strip().replace(",", ".")
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def _validate(self, _):
        value = self.value_or_none()
        valid = value is not None and self.minimum <= value <= self.maximum
        self.setProperty("invalid", "false" if valid else "true")
        self.style().unpolish(self)
        self.style().polish(self)
        self.validity_changed.emit(valid)
