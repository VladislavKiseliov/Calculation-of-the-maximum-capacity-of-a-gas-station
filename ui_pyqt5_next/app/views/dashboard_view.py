from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

try:
    import pyqtgraph as pg
except Exception:
    pg = None


class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(10)

        title = QLabel("Dashboard: пропускная способность и узкие места")
        title.setProperty("role", "heading")
        root.addWidget(title)

        cards = QHBoxLayout()
        cards.setSpacing(10)
        cards.addWidget(self._build_card("Qmax", "18 400 нм3/ч"))
        cards.addWidget(self._build_card("Критических участков", "3"))
        cards.addWidget(self._build_card("Сценарий", "Зима / Ночь"))
        root.addLayout(cards)

        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self.tabs, 1)

        chart_tab = QWidget()
        chart_layout = QVBoxLayout(chart_tab)
        chart_layout.setContentsMargins(8, 8, 8, 8)
        chart_layout.setSpacing(8)
        chart_layout.addWidget(QLabel("Падение давления вдоль линии"))
        self.chart_widget = self._build_chart()
        chart_layout.addWidget(self.chart_widget, 1)
        self.tabs.addTab(chart_tab, "График")

        critical_tab = QWidget()
        critical_layout = QVBoxLayout(critical_tab)
        critical_layout.setContentsMargins(8, 8, 8, 8)
        self.critical_table = QTableWidget(0, 4)
        self.critical_table.setHorizontalHeaderLabels(["Участок", "dP, МПа", "v, м/с", "Статус"])
        self.critical_table.horizontalHeader().setStretchLastSection(True)
        self.critical_table.verticalHeader().setVisible(False)
        self.critical_table.setAlternatingRowColors(True)
        critical_layout.addWidget(self.critical_table)
        self.tabs.addTab(critical_tab, "Критические зоны")

        self._fill_demo_critical()
        self._plot_demo()

    def _build_card(self, caption: str, value: str) -> QWidget:
        box = QFrame()
        box.setMinimumHeight(90)
        layout = QVBoxLayout(box)
        c = QLabel(caption)
        c.setProperty("role", "muted")
        v = QLabel(value)
        v.setProperty("role", "heading")
        layout.addWidget(c)
        layout.addWidget(v)
        return box

    def _build_chart(self):
        if pg is not None:
            plot = pg.PlotWidget()
            plot.setBackground((25, 34, 49))
            plot.showGrid(x=True, y=True, alpha=0.2)
            plot.setLabel("left", "dP, МПа")
            plot.setLabel("bottom", "Позиция вдоль линии")
            self._pg_plot = plot.plot([], [], pen=pg.mkPen(width=2, color="#2f7de1"), symbol="o")
            return plot
        fallback = QLabel("Установите pyqtgraph для интерактивного графика")
        fallback.setAlignment(Qt.AlignCenter)
        fallback.setProperty("role", "muted")
        return fallback

    def _plot_demo(self):
        x = [0, 1, 2, 3, 4, 5]
        y = [0.02, 0.04, 0.05, 0.09, 0.12, 0.15]
        if pg is not None:
            self._pg_plot.setData(x, y)

    def _fill_demo_critical(self):
        demo_rows: List[tuple] = [
            ("Участок A-01", 0.06, 14.2, "Норма"),
            ("Участок B-02", 0.11, 18.7, "Риск"),
            ("Участок C-07", 0.16, 22.1, "Критично"),
        ]
        self.critical_table.setRowCount(len(demo_rows))
        for i, row in enumerate(demo_rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                if j in (1, 2):
                    sev = float(value)
                    ratio = min(1.0, max(0.0, (sev - 0.05) / 0.15))
                    color = QColor(255, int(255 - 120 * ratio), int(130 - 90 * ratio))
                    item.setBackground(color)
                self.critical_table.setItem(i, j, item)
