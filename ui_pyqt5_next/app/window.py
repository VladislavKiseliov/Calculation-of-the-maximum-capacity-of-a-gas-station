import ctypes
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (
    QAction,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from .theme import build_stylesheet
from .views.dashboard_view import DashboardView
from .views.modules_view import ModulesView
from .views.tools_view import ToolsView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._titlebar_styled = False
        self.setWindowTitle("Gas Station Capacity - PyQt5 UI Prototype")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet(build_stylesheet(dark_mode=True))
        self._build_toolbar()
        self._build_layout()

    def _build_toolbar(self):
        toolbar = QToolBar("Main")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        icon_dir = Path(__file__).resolve().parents[1] / "assets" / "icons"
        save_icon = QIcon(str(icon_dir / "save.svg"))
        open_icon = QIcon(str(icon_dir / "open.svg"))
        calc_icon = QIcon(str(icon_dir / "calc.svg"))

        toolbar.addAction(QAction(save_icon, "Сохранить", self))
        toolbar.addAction(QAction(open_icon, "Импорт", self))
        toolbar.addSeparator()
        toolbar.addAction(QAction(calc_icon, "Запустить расчет", self))

    def _build_layout(self):
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)

        left = QWidget()
        left.setMinimumWidth(360)
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(8, 8, 8, 8)
        left_l.setSpacing(8)

        nav_title = QLabel("Навигация")
        nav_title.setProperty("role", "muted")
        left_l.addWidget(nav_title)

        self.nav = QListWidget()
        self.nav.addItems(["Dashboard", "Модули расчетов", "Инструментарий"])
        self.nav.setCurrentRow(0)
        left_l.addWidget(self.nav)

        tree_title = QLabel("Объекты проекта")
        tree_title.setProperty("role", "muted")
        left_l.addWidget(tree_title)

        self.tree = QTreeView()
        self.tree.setModel(self._build_tree_model())
        self.tree.expandAll()
        self.tree.setMinimumHeight(280)
        left_l.addWidget(self.tree, 1)

        self.object_label = QLabel("Выбран объект: -")
        self.object_label.setProperty("role", "muted")
        left_l.addWidget(self.object_label)

        add_title = QLabel("Добавить объект")
        add_title.setProperty("role", "muted")
        left_l.addWidget(add_title)

        add_form = QFormLayout()
        add_form.setContentsMargins(0, 0, 0, 0)
        add_form.setSpacing(6)

        self.object_type = QComboBox()
        self.object_type.addItems(["Труба", "Регулятор", "Котельная"])
        add_form.addRow("Тип:", self.object_type)

        self.object_name = QLineEdit()
        self.object_name.setPlaceholderText("Например: P-12, R-3, Boiler-1")
        add_form.addRow("Имя:", self.object_name)
        left_l.addLayout(add_form)

        actions = QHBoxLayout()
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self._add_object_to_tree)
        clear_button = QPushButton("Очистить")
        clear_button.setProperty("variant", "secondary")
        clear_button.clicked.connect(self.object_name.clear)
        actions.addWidget(add_button)
        actions.addWidget(clear_button)
        left_l.addLayout(actions)

        splitter.addWidget(left)

        self.pages = QStackedWidget()
        self.dashboard = DashboardView()
        self.modules = ModulesView()
        self.tools = ToolsView()
        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.modules)
        self.pages.addWidget(self.tools)
        splitter.addWidget(self.pages)

        self.modules.register_object("Труба P-01", "Труба")
        self.modules.register_object("Регулятор R-01", "Регулятор")
        self.modules.register_object("Котельная B-01", "Котельная")

        splitter.setSizes([420, 980])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.tree.clicked.connect(self._on_tree_clicked)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._titlebar_styled:
            self._apply_dark_title_bar()
            self._titlebar_styled = True

    def _build_tree_model(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Сеть/узлы"])

        station = QStandardItem("ГРС-01")
        self.pipes_root = QStandardItem("Трубы")
        self.regulators_root = QStandardItem("Регуляторы")
        self.boilers_root = QStandardItem("Котельные")

        self.pipes_root.appendRow(QStandardItem("Труба P-01"))
        self.regulators_root.appendRow(QStandardItem("Регулятор R-01"))
        self.boilers_root.appendRow(QStandardItem("Котельная B-01"))

        station.appendRow(self.pipes_root)
        station.appendRow(self.regulators_root)
        station.appendRow(self.boilers_root)
        model.appendRow(station)
        return model

    def _on_tree_clicked(self, index):
        value = str(index.data())
        self.object_label.setText(f"Выбран объект: {value}")
        if value.startswith("Труба "):
            self.modules.set_selected_object(value, "Труба")
        elif value.startswith("Регулятор "):
            self.modules.set_selected_object(value, "Регулятор")
        elif value.startswith("Котельная "):
            self.modules.set_selected_object(value, "Котельная")
        else:
            self.modules.set_selected_object(value, "Служебный узел")

    def _add_object_to_tree(self):
        raw_name = self.object_name.text().strip()
        if not raw_name:
            QMessageBox.warning(self, "Добавление объекта", "Введите имя объекта.")
            return

        selected_type = self.object_type.currentText()
        if selected_type == "Труба":
            parent = self.pipes_root
        elif selected_type == "Регулятор":
            parent = self.regulators_root
        else:
            parent = self.boilers_root

        typed_name = f"{selected_type} {raw_name}"
        parent.appendRow(QStandardItem(typed_name))
        self.modules.register_object(typed_name, selected_type)
        self.tree.expandAll()
        self.object_label.setText(f"Добавлен объект: {typed_name}")
        self.object_name.clear()

    def _apply_dark_title_bar(self):
        if sys.platform != "win32":
            return
        try:
            hwnd = int(self.winId())
            value = ctypes.c_int(1)
            set_attr = ctypes.windll.dwmapi.DwmSetWindowAttribute
            for attr in (20, 19):
                result = set_attr(hwnd, attr, ctypes.byref(value), ctypes.sizeof(value))
                if result == 0:
                    return
        except Exception:
            # Keep default frame if OS or theme API is unavailable.
            return
