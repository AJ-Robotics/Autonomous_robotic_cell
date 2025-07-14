# gui/calibration_wizard.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
from robodk.robomath import Mat
from vision.vision_utils import set_camera_to_robot_transform

class CalibrationWizard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibration Wizard: Vision ↔ Robot")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout()

        self.instructions = QLabel("Enter the 4x4 transformation matrix (T_camera_to_robot):")
        layout.addWidget(self.instructions)

        self.inputs = []
        for _ in range(4):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText("e.g., 1 0 0 0")
            layout.addWidget(line_edit)
            self.inputs.append(line_edit)

        self.apply_button = QPushButton("Apply Calibration")
        self.apply_button.clicked.connect(self.apply_transform)
        layout.addWidget(self.apply_button)

        self.setLayout(layout)

    def apply_transform(self):
        try:
            rows = []
            for line in self.inputs:
                values = list(map(float, line.text().strip().split()))
                if len(values) != 4:
                    raise ValueError("Each row must have 4 values")
                rows.append(values)

            mat_values = [rows[0], rows[1], rows[2], rows[3]]
            T = Mat(mat_values)
            set_camera_to_robot_transform(T)
            QMessageBox.information(self, "Success", "Calibration transform set successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Invalid input: {e}")
