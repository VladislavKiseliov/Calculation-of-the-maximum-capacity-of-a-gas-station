from typing import Dict

from PyQt5.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ..widgets.validated_input import ValidatedNumberInput
from .gas_composition_dialog import GasCompositionDialog


def _build_form(title: str, fields):
    box = QGroupBox(title)
    form = QFormLayout(box)
    form.setSpacing(8)
    created = {}
    for label, minimum, maximum, default in fields:
        w = ValidatedNumberInput(minimum=minimum, maximum=maximum)
        if default is not None:
            w.setText(str(default))
        form.addRow(label, w)
        created[label] = w
    return box, created


class ModulesView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_object_name = ""
        self.selected_object_type = ""
        self.object_params: Dict[str, Dict] = {}
        self.gas_state = {
            "gas_standard": "ГОСТ 5542-2014",
            "gas_mode": "Полный состав",
            "gas_composition": {},
        }

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(10)

        title = QLabel("Модули расчетов")
        title.setProperty("role", "heading")
        outer.addWidget(title)

        self.selected_object_label = QLabel("Параметры объекта: объект не выбран")
        self.selected_object_label.setProperty("role", "muted")
        outer.addWidget(self.selected_object_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll, 1)

        body = QWidget()
        scroll.setWidget(body)
        layout = QVBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs, 1)

        self._build_base_inputs_tab()
        self._build_pipe_tab()
        self._build_regulator_tab()
        self._build_boiler_tab()

        actions = QHBoxLayout()
        save_current = QPushButton("Сохранить параметры выбранного объекта")
        save_current.clicked.connect(self._save_current_tab_for_selected_object)
        run_calc = QPushButton("Автоматический расчет")
        run_calc.setProperty("variant", "secondary")
        run_calc.clicked.connect(self._mock_run_calculation)
        actions.addWidget(save_current)
        actions.addWidget(run_calc)
        actions.addStretch(1)
        layout.addLayout(actions)

    def register_object(self, object_name: str, object_type: str):
        if object_name in self.object_params:
            return
        if object_type == "Труба":
            values = {k: v.value_or_none() for k, v in self.pipe_inputs.items()}
        elif object_type == "Регулятор":
            values = {k: v.value_or_none() for k, v in self.reg_inputs.items()}
        elif object_type == "Котельная":
            values = {k: v.value_or_none() for k, v in self.boiler_inputs.items()}
        else:
            values = {}
        self.object_params[object_name] = {"type": object_type, "values": values}

    def set_selected_object(self, object_name: str, object_type: str):
        self.selected_object_name = object_name
        self.selected_object_type = object_type
        self.selected_object_label.setText(f"Параметры объекта: {object_name} ({object_type})")
        self._load_selected_object_values()

        if object_type == "Труба":
            self.tabs.setCurrentIndex(1)
        elif object_type == "Регулятор":
            self.tabs.setCurrentIndex(2)
        elif object_type == "Котельная":
            self.tabs.setCurrentIndex(3)

    def get_calculation_payload(self):
        return {
            "base_inputs": {k: v.value_or_none() for k, v in self.base_inputs.items()},
            "gas_standard": self.gas_state["gas_standard"],
            "gas_mode": self.gas_state["gas_mode"],
            "gas_composition": self.gas_state["gas_composition"],
            "object_parameters": self.object_params,
        }

    def _build_base_inputs_tab(self):
        page = QWidget()
        page_l = QVBoxLayout(page)

        base_box, self.base_inputs = _build_form(
            "Основные параметры расчета",
            [
                ("Температура на входе, °C", -273.0, 500.0, None),
                ("Температура на выходе, °C", -273.0, 500.0, None),
                ("Давление на входе, МПа", 0.0, 50.0, None),
                ("Давление на выходе, МПа", 0.0, 50.0, None),
            ],
        )
        page_l.addWidget(base_box)

        gas_box = QGroupBox("Состав газа")
        gas_l = QVBoxLayout(gas_box)
        self.gas_summary = QLabel("")
        self.gas_summary.setProperty("role", "muted")
        gas_l.addWidget(self.gas_summary)
        configure = QPushButton("Открыть подменю состава газа")
        configure.clicked.connect(self._open_gas_dialog)
        gas_l.addWidget(configure)
        page_l.addWidget(gas_box)
        self._refresh_gas_summary()

        save_base = QPushButton("Сохранить базовые параметры")
        save_base.clicked.connect(self._save_base_inputs)
        page_l.addWidget(save_base)
        page_l.addStretch(1)

        self.tabs.addTab(page, "Основные параметры")

    def _build_pipe_tab(self):
        page = QWidget()
        l = QVBoxLayout(page)
        box, self.pipe_inputs = _build_form(
            "Параметры трубы",
            [
                ("Диаметр, мм", 1.0, 5000.0, None),
                ("Толщина стенки, мм", 0.1, 100.0, None),
                ("Длина, м", 0.1, 100000.0, None),
                ("Шероховатость, мм", 0.0, 10.0, 0.03),
                ("Расход, нм3/ч", 0.0, 100000000.0, None),
            ],
        )
        l.addWidget(box)
        l.addWidget(QPushButton("Рассчитать трубу"))
        l.addStretch(1)
        self.tabs.addTab(page, "Трубы")

    def _build_regulator_tab(self):
        page = QWidget()
        l = QVBoxLayout(page)
        box, self.reg_inputs = _build_form(
            "Параметры регулятора",
            [
                ("Pin, МПа", 0.0, 50.0, None),
                ("Pout, МПа", 0.0, 50.0, None),
                ("Kv", 0.0, 100000.0, None),
                ("Количество линий", 1.0, 100.0, 1.0),
            ],
        )
        l.addWidget(box)
        l.addWidget(QPushButton("Рассчитать регулятор"))
        l.addStretch(1)
        self.tabs.addTab(page, "Регуляторы")

    def _build_boiler_tab(self):
        page = QWidget()
        l = QVBoxLayout(page)
        box, self.boiler_inputs = _build_form(
            "Параметры котельной",
            [
                ("Мощность котельной, кВт", 0.0, 1000000.0, None),
                ("Tin, °C", -273.0, 500.0, None),
                ("Tout, °C", -273.0, 500.0, None),
                ("КПД, %", 1.0, 100.0, 90.0),
            ],
        )
        l.addWidget(box)
        l.addWidget(QPushButton("Рассчитать котельную"))
        l.addStretch(1)
        self.tabs.addTab(page, "Котельные")

    def _open_gas_dialog(self):
        dlg = GasCompositionDialog(state=self.gas_state, parent=self)
        if dlg.exec_() and dlg.is_saved():
            self.gas_state = dlg.get_state()
            self._refresh_gas_summary()

    def _refresh_gas_summary(self):
        comp = self.gas_state.get("gas_composition", {}) or {}
        total = sum(v for v in comp.values() if v is not None) if comp else 0.0
        self.gas_summary.setText(
            f"Стандарт: {self.gas_state['gas_standard']} | Режим: {self.gas_state['gas_mode']} | "
            f"Компонентов: {len(comp)} | Сумма: {total:.3f}%"
        )

    def _save_base_inputs(self):
        invalid = [name for name, field in self.base_inputs.items() if field.value_or_none() is None]
        if invalid:
            QMessageBox.warning(self, "Основные параметры", f"Проверьте поля: {', '.join(invalid)}")
            return
        comp = self.gas_state.get("gas_composition", {})
        total = sum(v for v in comp.values() if v is not None) if comp else 0.0
        if abs(total - 100.0) > 0.01:
            QMessageBox.warning(self, "Состав газа", "Сначала задайте состав газа с суммой 100% в подменю.")
            return
        QMessageBox.information(self, "Основные параметры", "Базовые параметры сохранены.")

    def _set_fields(self, fields: Dict[str, ValidatedNumberInput], values: Dict[str, float]):
        for name, field in fields.items():
            value = values.get(name)
            field.setText("" if value is None else str(value))

    def _load_selected_object_values(self):
        stored = self.object_params.get(self.selected_object_name)
        if not stored:
            return
        values = stored.get("values", {})
        kind = stored.get("type")
        if kind == "Труба":
            self._set_fields(self.pipe_inputs, values)
        elif kind == "Регулятор":
            self._set_fields(self.reg_inputs, values)
        elif kind == "Котельная":
            self._set_fields(self.boiler_inputs, values)

    def _save_current_tab_for_selected_object(self):
        if self.selected_object_type not in ("Труба", "Регулятор", "Котельная"):
            QMessageBox.warning(self, "Сохранение параметров", "Выберите конкретный объект (труба/регулятор/котельная) в дереве.")
            return
        tab = self.tabs.currentIndex()
        if tab == 1 and self.selected_object_type == "Труба":
            values = {k: v.value_or_none() for k, v in self.pipe_inputs.items()}
        elif tab == 2 and self.selected_object_type == "Регулятор":
            values = {k: v.value_or_none() for k, v in self.reg_inputs.items()}
        elif tab == 3 and self.selected_object_type == "Котельная":
            values = {k: v.value_or_none() for k, v in self.boiler_inputs.items()}
        else:
            QMessageBox.warning(self, "Сохранение параметров", "Откройте вкладку соответствующего типа объекта и сохраните.")
            return
        self.object_params[self.selected_object_name] = {"type": self.selected_object_type, "values": values}
        QMessageBox.information(self, "Сохранение параметров", f"Сохранено для {self.selected_object_name}")

    def _mock_run_calculation(self):
        payload = self.get_calculation_payload()
        QMessageBox.information(
            self,
            "Расчет",
            f"Готово к расчету.\nОбъектов с параметрами: {len(payload['object_parameters'])}\n"
            f"Стандарт газа: {payload['gas_standard']}",
        )
