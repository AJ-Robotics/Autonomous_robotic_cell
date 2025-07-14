# main_ui.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QInputDialog, QSpinBox, QDialog, QRubberBand,
    QScrollArea, QSizePolicy, QGroupBox, QGridLayout, QSpacerItem
)
from PyQt5.QtCore import QTimer, Qt, QRect, QPoint, QSize
from PyQt5.QtGui import QPixmap, QImage
import cv2

from vision.camera_handler import CameraHandler
from vision.qr_detector import QRDetector
from vision.object_detector import ObjectDetector
from vision.vision_utils import pixel_to_mm, set_calibration_scale, vision_to_robot_coords
from robot.robodk_handler import RoboDKHandler
from robot.path_planner import PathPlanner
from gui.object_panel import ObjectPanel
from gui.calibration_wizard import CalibrationWizard


camera = CameraHandler()
qr_detector = QRDetector()
object_detector = ObjectDetector()
robodk = RoboDKHandler()
planner = PathPlanner()


class TeachDialog(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Teach Object Orientation")
        self.setGeometry(200, 200, 640, 480)
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap.fromImage(image))
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)


class ROISelector(QDialog):
    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select ROI")
        self.setGeometry(300, 300, 800, 600)
        self.image = image
        self.label = QLabel()
        self.label.setPixmap(QPixmap.fromImage(image))
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self.label)
        self.origin = QPoint()
        self.label.mousePressEvent = self.start_selection
        self.label.mouseMoveEvent = self.update_selection
        self.label.mouseReleaseEvent = self.finish_selection
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.roi = None

    def start_selection(self, event):
        self.origin = event.pos()
        self.rubberBand.setGeometry(QRect(self.origin, QSize()))
        self.rubberBand.show()

    def update_selection(self, event):
        self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def finish_selection(self, event):
        self.roi = self.rubberBand.geometry()
        self.accept()


class MainUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Autonomous Robotic Cell")
        self.setMinimumSize(1000, 600)

        self.image_label = QLabel()
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.captured_label = QLabel()
        self.captured_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Object panel
        self.object_panel = ObjectPanel()
        self.object_panel.object_selected.connect(self.on_object_selected)

        # Operation + camera + sliders
        self.operation_combo = QComboBox()
        self.operation_combo.addItems(["Pick", "Move", "Place"])
        self.camera_combo = QComboBox()
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 255)
        self.gain_slider = QSlider(Qt.Horizontal)
        self.gain_slider.setRange(0, 255)
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setRange(0, 255)
        self.origin_x_spin = QSpinBox()
        self.origin_x_spin.setRange(0, 1000)
        self.origin_x_spin.setValue(50)
        self.origin_y_spin = QSpinBox()
        self.origin_y_spin.setRange(0, 1000)
        self.origin_y_spin.setValue(50)

        # Buttons
        self.capture_button = QPushButton("📸 Capture")
        self.detect_button = QPushButton("🎯 Detect")
        self.execute_button = QPushButton("🤖 Execute")
        self.simulate_button = QPushButton("🧪 Simulate")
        self.calibrate_button = QPushButton("📏 Calibration Scale")
        self.wizard_button = QPushButton("🧙 Calibration Wizard")
        self.teach_button = QPushButton("📍 Teach Position")
        self.teach_obj_button = QPushButton("🧠 Teach Object")
        self.set_roi_button = QPushButton("🔲 Set ROI")
        self.playback_button = QPushButton("▶️ Playback")
        self.clear_button = QPushButton("❌ Clear Taught")
        self.refresh_cameras_button = QPushButton("🔄 Refresh Cameras")

        # Group controls in grid
        controls_layout = QGridLayout()
        controls_layout.addWidget(QLabel("X-Origin Offset:"), 0, 0)
        controls_layout.addWidget(self.origin_x_spin, 0, 1)
        controls_layout.addWidget(QLabel("Y-Origin Offset:"), 1, 0)
        controls_layout.addWidget(self.origin_y_spin, 1, 1)
        controls_layout.addWidget(QLabel("Operation:"), 2, 0)
        controls_layout.addWidget(self.operation_combo, 2, 1)
        controls_layout.addWidget(QLabel("Camera:"), 3, 0)
        controls_layout.addWidget(self.camera_combo, 3, 1)
        controls_layout.addWidget(self.refresh_cameras_button, 4, 0, 1, 2)
        controls_layout.addWidget(QLabel("Brightness"), 5, 0)
        controls_layout.addWidget(self.brightness_slider, 5, 1)
        controls_layout.addWidget(QLabel("Gain"), 6, 0)
        controls_layout.addWidget(self.gain_slider, 6, 1)
        controls_layout.addWidget(QLabel("Exposure"), 7, 0)
        controls_layout.addWidget(self.exposure_slider, 7, 1)

        # Buttons group
        button_group = QVBoxLayout()
        for btn in [self.calibrate_button, self.wizard_button, self.capture_button,
                    self.detect_button, self.execute_button, self.simulate_button,
                    self.teach_button, self.teach_obj_button, self.set_roi_button,
                    self.playback_button, self.clear_button]:
            btn.setMinimumHeight(32)
            btn.setStyleSheet("QPushButton { font-weight: bold; }")
            button_group.addWidget(btn)

        # Final controls layout
        group = QVBoxLayout()
        group.addLayout(controls_layout)
        group.addLayout(button_group)
        group.addWidget(QLabel("🧠 Select Object:"))
        group.addWidget(self.object_panel)
        group.addStretch()

        scroll_widget = QWidget()
        scroll_widget.setLayout(group)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        # Image panels
        image_layout = QVBoxLayout()
        image_layout.addWidget(QLabel("🔴 Live Feed"))
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(QLabel("🟡 Captured Frame"))
        image_layout.addWidget(self.captured_label)

        main_layout = QHBoxLayout()
        main_layout.addLayout(image_layout, 3)
        main_layout.addWidget(scroll_area, 1)
        self.setLayout(main_layout)

        # Connections
        self.capture_button.clicked.connect(self.capture_frame)
        self.detect_button.clicked.connect(self.detect_objects)
        self.execute_button.clicked.connect(self.execute_task)
        self.simulate_button.clicked.connect(self.simulate_task)
        self.calibrate_button.clicked.connect(self.set_calibration)
        self.wizard_button.clicked.connect(self.open_calibration_wizard)
        self.teach_button.clicked.connect(self.teach_position)
        self.teach_obj_button.clicked.connect(self.open_teach_object_window)
        self.set_roi_button.clicked.connect(self.set_camera_roi)
        self.playback_button.clicked.connect(self.playback_positions)
        self.clear_button.clicked.connect(self.clear_positions)
        self.refresh_cameras_button.clicked.connect(self.refresh_camera_list)
        self.camera_combo.currentIndexChanged.connect(self.switch_camera)
        self.brightness_slider.valueChanged.connect(lambda val: camera.set_brightness(val))
        self.gain_slider.valueChanged.connect(lambda val: camera.set_gain(val))
        self.exposure_slider.valueChanged.connect(lambda val: camera.set_exposure(val))

        # Live update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.selected_object = None
        self.last_detected_objects = []
        self.should_draw_objects = False
        self.captured_image = None
        self.refresh_camera_list()

    def get_user_origin(self):
        h = 720
        frame = camera.get_frame()
        if frame is not None:
            h = frame.shape[0]
        ox = self.origin_x_spin.value()
        oy = h - self.origin_y_spin.value()
        return ox, oy

    def refresh_camera_list(self):
        self.camera_combo.clear()
        for i in self.get_available_cameras():
            self.camera_combo.addItem(f"Camera {i}", i)

    def get_available_cameras(self, max_tested=5):
        available = []
        for i in range(max_tested):
            cap = cv2.VideoCapture(i)
            if cap and cap.isOpened():
                available.append(i)
                cap.release()
        return available

    def switch_camera(self):
        index = self.camera_combo.currentData()
        if index is not None:
            camera.set_camera_index(index)
            camera.set_brightness(self.brightness_slider.value())
            camera.set_gain(self.gain_slider.value())
            camera.set_exposure(self.exposure_slider.value())

    def update_frame(self):
        frame = camera.get_frame()
        if frame is not None:
            display = frame.copy()
            ox, oy = self.get_user_origin()

            cv2.arrowedLine(display, (ox, oy), (ox + 100, oy), (0, 0, 255), 2)
            cv2.putText(display, 'X', (ox + 110, oy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.arrowedLine(display, (ox, oy), (ox, oy - 100), (0, 255, 0), 2)
            cv2.putText(display, 'Y', (ox - 10, oy - 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if self.should_draw_objects:
                for obj in self.last_detected_objects:
                    px, py = obj['coords']
                    adj_x = px - ox
                    adj_y = oy - py  # <--- Inverted Y-axis
                    if 'contour' in obj:
                        cv2.drawContours(display, [obj['contour']], -1, (0, 255, 255), 2)
                    cv2.circle(display, (px, py), 5, (0, 255, 0), -1)
                    cv2.putText(display, f"{obj['label']} ({adj_x},{adj_y})", (px + 5, py - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
                    if obj == self.selected_object:
                        cv2.rectangle(display, (px - 10, py - 10), (px + 10, py + 10), (255, 255, 0), 2)

            self.image_label.setPixmap(self.convert_cv_qt(display))

    def detect_objects(self):
        frame = camera.get_frame()
        if frame is not None:
            objects, _ = object_detector.detect_objects(frame)
            self.last_detected_objects = objects
            self.object_panel.update_objects(objects)
            self.should_draw_objects = True
            self.captured_image = frame.copy()
            self.captured_label.setPixmap(self.convert_cv_qt(self.captured_image))

    def convert_cv_qt(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image)

    def capture_frame(self):
        frame = camera.get_frame()
        if frame is not None:
            cv2.imwrite("assets/capture.jpg", frame)

    def execute_task(self):
        if not self.selected_object:
            print("No object selected.")
            return
        px, py = self.selected_object['coords']
        ox, oy = self.get_user_origin()
        adj_x = px - ox
        adj_y = oy - py  # <--- Inverted Y-axis
        coords_mm = pixel_to_mm((adj_x, adj_y))
        pose = vision_to_robot_coords(*coords_mm)
        path = planner.generate_path(self.operation_combo.currentText(), pose)
        robodk.execute_path(path)

    def simulate_task(self):
        if not self.selected_object:
            print("No object selected.")
            return
        px, py = self.selected_object['coords']
        ox, oy = self.get_user_origin()
        adj_x = px - ox
        adj_y = oy - py  # <--- Inverted Y-axis
        coords_mm = pixel_to_mm((adj_x, adj_y))
        pose = vision_to_robot_coords(*coords_mm)
        path = planner.generate_path(self.operation_combo.currentText(), [pose])
        robodk.simulate_path(path)

    def set_calibration(self):
        scale, ok = QInputDialog.getDouble(self, "Set Calibration Scale", "Enter mm per pixel:",
                                           decimals=6, min=0.0001, max=100.0)
        if ok:
            set_calibration_scale(scale)

    def open_calibration_wizard(self):
        self.wizard = CalibrationWizard()
        self.wizard.show()

    def teach_position(self):
        robodk.teach_current_position()

    def playback_positions(self):
        if robodk.has_taught_positions():
            robodk.playback_taught_positions()

    def clear_positions(self):
        robodk.clear_taught_positions()

    def set_camera_roi(self):
        frame = camera.get_frame()
        if frame is not None:
            img = self.convert_cv_qt(frame).toImage()
            roi_selector = ROISelector(img, self)
            if roi_selector.exec_():
                roi = roi_selector.roi

    def open_teach_object_window(self):
        if self.captured_image is not None:
            img = self.convert_cv_qt(self.captured_image).toImage()
            dlg = TeachDialog(img, self)
            dlg.exec_()

    def on_object_selected(self, obj_data):
        self.selected_object = obj_data

    def closeEvent(self, event):
        self.timer.stop()
        camera.release()
        super().closeEvent(event)


def launch_gui():
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec_())