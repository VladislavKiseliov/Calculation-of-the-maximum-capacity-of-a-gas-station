def build_stylesheet(dark_mode: bool = True) -> str:
    if dark_mode:
        bg = "#10151c"
        panel = "#192231"
        text = "#e6edf7"
        muted = "#9aa7ba"
        border = "#2a3a50"
        accent = "#2f7de1"
        accent_hover = "#3f8df0"
        invalid = "#3b1d22"
    else:
        bg = "#eef2f8"
        panel = "#ffffff"
        text = "#172033"
        muted = "#6d7a8f"
        border = "#cfdae8"
        accent = "#2f7de1"
        accent_hover = "#3f8df0"
        invalid = "#fde8eb"

    return f"""
    QWidget {{
        background: {bg};
        color: {text};
        font-family: "Segoe UI", "Roboto", sans-serif;
        font-size: 13px;
    }}
    QMainWindow, QFrame, QGroupBox, QTreeView, QTableWidget, QTabWidget::pane {{
        background: {panel};
        border: 1px solid {border};
        border-radius: 8px;
    }}
    QGroupBox {{
        margin-top: 10px;
        padding-top: 10px;
        font-weight: 600;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px 0 4px;
        color: {muted};
    }}
    QPushButton {{
        background: {accent};
        color: #ffffff;
        border: 0;
        border-radius: 6px;
        padding: 8px 12px;
        font-weight: 600;
        min-height: 18px;
    }}
    QPushButton:hover {{
        background: {accent_hover};
    }}
    QPushButton[variant="secondary"] {{
        background: transparent;
        color: {text};
        border: 1px solid {border};
    }}
    QPushButton[variant="secondary"]:hover {{
        background: {panel};
    }}
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
        border: 1px solid {border};
        border-radius: 6px;
        padding: 6px;
        background: {panel};
    }}
    QLineEdit[invalid="true"] {{
        border: 1px solid #ef4444;
        background: {invalid};
    }}
    QLabel[role="heading"] {{
        font-size: 18px;
        font-weight: 700;
    }}
    QLabel[role="muted"] {{
        color: {muted};
    }}
    QHeaderView::section {{
        background: {panel};
        color: {muted};
        border: 0;
        border-bottom: 1px solid {border};
        padding: 6px;
        font-weight: 600;
    }}
    QTabWidget::pane {{
        margin-top: 6px;
    }}
    QTabBar::tab {{
        background: {panel};
        border: 1px solid {border};
        border-bottom: 0;
        padding: 8px 12px;
        margin-right: 4px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}
    QTabBar::tab:selected {{
        background: {accent};
        color: #ffffff;
    }}
    QListWidget {{
        border: 0;
        background: transparent;
    }}
    QListWidget::item {{
        padding: 8px;
        border-radius: 6px;
        margin: 2px;
    }}
    QListWidget::item:selected {{
        background: {accent};
        color: #ffffff;
    }}
    QSplitter::handle {{
        background: {border};
        width: 2px;
    }}
    """
