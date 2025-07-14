# vision/vision_utils.py
from robodk.robomath import Mat, transl, rotz

# Default calibration values
calibration_scale = 1.0  # mm per pixel

# Transformation from vision space to robot space (identity by default)
T_cam_to_robot = Mat([[1, 0, 0, 0],
                      [0, 1, 0, 0],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]])

def set_calibration_scale(scale):
    global calibration_scale
    calibration_scale = scale

def get_calibration_scale():
    return calibration_scale

def pixel_to_mm(pixel_coords):
    x_px, y_px = pixel_coords
    x_mm = round(x_px * calibration_scale, 2)
    y_mm = round(y_px * calibration_scale, 2)
    return (x_mm, y_mm)

def mm_to_pixel(mm_coords):
    x_mm, y_mm = mm_coords
    x_px = int(x_mm / calibration_scale)
    y_px = int(y_mm / calibration_scale)
    return (x_px, y_px)

def set_camera_to_robot_transform(mat: Mat):
    global T_cam_to_robot
    T_cam_to_robot = mat

def vision_to_robot_coords(x_mm, y_mm, z_mm=0.0, angle_deg=0.0):
    """
    Convert a 2D vision point (in mm) + angle to robot coordinates (as a pose).
    Applies transformation using the calibrated camera-to-robot matrix.
    """
    pose_vision = transl(x_mm, y_mm, z_mm) * rotz(angle_deg * 3.14159 / 180.0)
    pose_robot = T_cam_to_robot * pose_vision
    return pose_robot
