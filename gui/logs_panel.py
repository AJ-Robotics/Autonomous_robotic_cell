from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from datetime import datetime

class LogsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.label = QLabel("Logs:")
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.log_box)
        self.setLayout(self.layout)

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level.upper()}] {message}"
        self.log_box.append(formatted)
        print(formatted)  # optional: also print to console

    def clear_logs(self):
        self.log_box.clear()
