from PyQt5.QtWidgets import QWidget, QListWidget, QVBoxLayout
from PyQt5.QtCore import pyqtSignal

class ObjectPanel(QWidget):
    object_selected = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.list_widget = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
        self.objects = []

        self.list_widget.currentRowChanged.connect(self.on_selection_changed)

    def update_objects(self, objects):
        self.list_widget.clear()
        self.objects = objects
        for i, obj in enumerate(objects):
            label = obj.get("label", f"Object{i+1}")
            coords = obj.get("coords", (0, 0))
            self.list_widget.addItem(f"{label} ({coords[0]}, {coords[1]})")

    def on_selection_changed(self, index):
        if 0 <= index < len(self.objects):
            self.object_selected.emit(self.objects[index])
