from typing import Dict, Tuple

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..widgets.validated_input import ValidatedNumberInput


class GasCompositionDialog(QDialog):
    def __init__(self, state=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Состав газа")
        self.resize(720, 700)
        self._saved = False

        self._state = state or {
            "gas_standard": "ГОСТ 5542-2014",
            "gas_mode": "Полный состав",
            "gas_composition": {},
        }

        root = QVBoxLayout(self)
        root.setSpacing(10)

        header = QGroupBox("Настройки состава газа")
        header_form = QFormLayout(header)
        self.gost_combo = QComboBox()
        self.gost_combo.addItems(["ГОСТ 5542-2014", "ГОСТ 31371.7-2008"])
        self.gost_combo.currentIndexChanged.connect(self._sync_mode_with_gost)
        header_form.addRow("Стандарт:", self.gost_combo)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Полный состав", "Азот + Примесь-X"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        header_form.addRow("Режим:", self.mode_combo)
        root.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        root.addWidget(scroll, 1)

        container = QWidget()
        scroll.setWidget(container)
        container_layout = QVBoxLayout(container)

        self.stack = QStackedWidget()
        self.full_box, self.full_inputs = self._build_full_gas_box()
        self.simple_box, self.simple_inputs = self._build_simple_gas_box()
        self.stack.addWidget(self.full_box)
        self.stack.addWidget(self.simple_box)
        container_layout.addWidget(self.stack)

        self.sum_label = QLabel("")
        self.sum_label.setProperty("role", "muted")
        container_layout.addWidget(self.sum_label)
        container_layout.addStretch(1)

        buttons = QHBoxLayout()
        norm = QPushButton("Нормировать до 100%")
        norm.setProperty("variant", "secondary")
        norm.clicked.connect(self._normalize_current)
        save = QPushButton("Сохранить состав")
        save.clicked.connect(self._save_and_close)
        cancel = QPushButton("Отмена")
        cancel.setProperty("variant", "secondary")
        cancel.clicked.connect(self.reject)
        buttons.addWidget(norm)
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        root.addLayout(buttons)

        self._apply_initial_state()

    def get_state(self):
        return {
            "gas_standard": self.gost_combo.currentText(),
            "gas_mode": self.mode_combo.currentText(),
            "gas_composition": self._current_composition(),
        }

    def is_saved(self):
        return self._saved

    def _build_full_gas_box(self) -> Tuple[QWidget, Dict[str, ValidatedNumberInput]]:
        components = [
            ("Метан CH4", 95.0), ("Этан C2H6", 5.0), ("Пропан C3H8", 0.0),
            ("н-Бутан n-C4H10", 0.0), ("и-Бутан i-C4H10", 0.0), ("н-Пентан n-C5H12", 0.0),
            ("и-Пентан i-C5H12", 0.0), ("н-Гексан n-C6H14", 0.0), ("н-Гептан n-C7H16", 0.0),
            ("н-Октан n-C8H18", 0.0), ("Ацетилен C2H2", 0.0), ("Этилен C2H4", 0.0),
            ("Пропилен C3H6", 0.0), ("Бензол C6H6", 0.0), ("Толуол C7H8", 0.0),
            ("Водород H2", 0.0), ("Водяной пар H2O", 0.0), ("Аммиак NH3", 0.0),
            ("Метанол CH3OH", 0.0), ("Сероводород H2S", 0.0), ("Метилмеркаптан CH3SH", 0.0),
            ("Диоксид серы SO2", 0.0), ("Гелий He", 0.0), ("Неон Ne", 0.0),
            ("Аргон Ar", 0.0), ("Моноксид углерода CO", 0.0), ("Азот N2", 0.0),
            ("Воздух", 0.0), ("Кислород O2", 0.0), ("Диоксид углерода CO2", 0.0),
        ]
        box = QGroupBox("Полный состав, % об.")
        form = QFormLayout(box)
        form.setSpacing(6)
        inputs = {}
        for name, default in components:
            field = ValidatedNumberInput(minimum=0.0, maximum=100.0)
            field.setText(str(default))
            field.textChanged.connect(self._update_sum)
            inputs[name] = field
            form.addRow(name + ":", field)
        return box, inputs

    def _build_simple_gas_box(self) -> Tuple[QWidget, Dict[str, ValidatedNumberInput]]:
        box = QGroupBox("Упрощенный состав, % об.")
        form = QFormLayout(box)
        inputs = {}
        for name, default in [("Азот N2", 99.0), ("Примесь-X", 1.0)]:
            field = ValidatedNumberInput(minimum=0.0, maximum=100.0)
            field.setText(str(default))
            field.textChanged.connect(self._update_sum)
            inputs[name] = field
            form.addRow(name + ":", field)
        return box, inputs

    def _apply_initial_state(self):
        std = self._state.get("gas_standard", "ГОСТ 5542-2014")
        mode = self._state.get("gas_mode", "Полный состав")
        comp = self._state.get("gas_composition", {}) or {}
        self.gost_combo.setCurrentText(std)
        self.mode_combo.setCurrentText(mode)
        self._on_mode_changed()
        for name, value in comp.items():
            field = self.full_inputs.get(name) or self.simple_inputs.get(name)
            if field is not None and value is not None:
                field.setText(str(value))
        self._update_sum()

    def _sync_mode_with_gost(self):
        if self.gost_combo.currentText() == "ГОСТ 5542-2014":
            self.mode_combo.setCurrentText("Полный состав")
        else:
            self.mode_combo.setCurrentText("Азот + Примесь-X")
        self._on_mode_changed()

    def _on_mode_changed(self):
        self.stack.setCurrentIndex(0 if self.mode_combo.currentText() == "Полный состав" else 1)
        self._update_sum()

    def _active_inputs(self):
        return self.full_inputs if self.stack.currentIndex() == 0 else self.simple_inputs

    def _current_composition(self):
        return {k: v.value_or_none() for k, v in self._active_inputs().items()}

    def _sum_value(self):
        return sum(0.0 if v.value_or_none() is None else max(0.0, v.value_or_none()) for v in self._active_inputs().values())

    def _update_sum(self):
        total = self._sum_value()
        suffix = "(OK)" if abs(total - 100.0) <= 0.01 else "(нужно 100%)"
        self.sum_label.setText(f"Сумма состава: {total:.3f} % {suffix}")

    def _normalize_current(self):
        fields = self._active_inputs()
        vals = {k: (0.0 if f.value_or_none() is None else max(0.0, f.value_or_none())) for k, f in fields.items()}
        total = sum(vals.values())
        if total <= 0.0:
            QMessageBox.warning(self, "Состав газа", "Нечего нормировать: сумма равна 0.")
            return
        for k, f in fields.items():
            f.setText(f"{(vals[k] * 100.0 / total):.6f}")
        self._update_sum()

    def _save_and_close(self):
        if abs(self._sum_value() - 100.0) > 0.01:
            QMessageBox.warning(self, "Состав газа", "Сумма состава должна быть 100%.")
            return
        self._saved = True
        self.accept()
