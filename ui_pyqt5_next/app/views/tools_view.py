from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ToolsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(10)

        title = QLabel("Инструментарий и подбор оборудования")
        title.setProperty("role", "heading")
        root.addWidget(title)

        top = QHBoxLayout()
        top.setSpacing(10)
        root.addLayout(top, 1)

        refs = QGroupBox("Справочники")
        refs.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        refs_l = QVBoxLayout(refs)
        lst = QListWidget()
        for item in [
            "ГОСТ: трубы стальные",
            "Справочник: плотность газов",
            "База: регуляторы давления",
            "База: диаметры труб",
        ]:
            lst.addItem(QListWidgetItem(item))
        refs_l.addWidget(lst, 1)
        refs_button = QPushButton("Открыть справочник")
        refs_button.setProperty("variant", "secondary")
        refs_l.addWidget(refs_button)
        top.addWidget(refs, 1)

        compare = QGroupBox("Режим сравнения: текущее vs рекомендуемое")
        compare.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        compare_l = QVBoxLayout(compare)
        self.table = QTableWidget(4, 4)
        self.table.setHorizontalHeaderLabels(["Параметр", "Текущее", "Рекомендуемое", "Δ"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        demo = [
            ("Kv", "45", "60", "+15"),
            ("Диаметр, мм", "100", "125", "+25"),
            ("Скорость, м/с", "21.3", "17.8", "-3.5"),
            ("Тепл. мощность, кВт", "280", "320", "+40"),
        ]
        for i, row in enumerate(demo):
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(value))
        compare_l.addWidget(self.table, 1)
        compare_l.addWidget(QPushButton("Подобрать автоматически"))
        top.addWidget(compare, 2)
