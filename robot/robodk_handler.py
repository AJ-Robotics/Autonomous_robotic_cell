# robot/robodk_handler.py

from robodk import robolink, robomath

class RoboDKHandler:
    def __init__(self):
        self.RDK = robolink.Robolink()
        self.robot = self.RDK.Item('JAKA Zu5', robolink.ITEM_TYPE_ROBOT)

        if not self.robot.Valid():
            raise Exception("❌ JAKA Zu5 robot not found in the RoboDK station. Please load or rename correctly.")

        self.taught_positions = []
        self.taught_object_poses = []

    def _safe_target_pose(self, pose):
        """Ensure pose has a rotation applied (e.g., align Z tool axis if needed)"""
        return pose * robomath.roty(3.14)

    def _pose_with_rotation(self, pose, angle_deg):
        """Apply Z rotation (around tool axis) to pose"""
        rz = robomath.rotz(angle_deg * 3.14159265 / 180.0)
        return pose * rz

    def execute_path(self, path):
        for pose in path:
            target = self._safe_target_pose(pose)
            joints = self.robot.SolveIK(target)
            if joints is None or joints.size(1) == 0:
                print(f"[RoboDKHandler] ❌ Cannot reach pose: {target.Pos()}")
                continue
            self.robot.MoveL(joints)

    def simulate_path(self, path):
        for pose in path:
            target = self._safe_target_pose(pose)
            joints = self.robot.SolveIK(target)
            if joints is None or joints.size(1) == 0:
                print(f"[RoboDKHandler] ❌ Cannot reach pose (SIM): {target.Pos()}")
                continue
            self.robot.MoveJ(joints)

    def teach_current_position(self):
        if not self.robot.Valid():
            print("❌ Robot is not valid. Cannot teach position.")
            return

        joints = self.robot.Joints()
        name = f"TaughtPos_{len(self.RDK.ItemList(robolink.ITEM_TYPE_TARGET))}"

        # Safe fallback for robot frame
        robot_frame = self.robot.Parent()
        if not robot_frame.Valid():
            print("⚠️ Robot frame invalid, using station root as parent.")
            robot_frame = self.RDK.Item('', robolink.ITEM_TYPE_FRAME)

        target = self.RDK.AddTarget(name, self.robot, robot_frame)
        if not target.Valid():
            print(f"❌ Failed to create target '{name}'")
            return

        target.setAsJointTarget()
        target.setJoints(joints)
        self.taught_positions.append(joints)
        print(f"[✔] Position '{name}' saved at joints: {joints}")

    def playback_taught_positions(self):
        for joints in self.taught_positions:
            self.robot.MoveJ(joints)
            print(f"[RoboDKHandler] ▶️ Playing back position: {joints}")

    def clear_taught_positions(self):
        self.taught_positions.clear()
        print("[RoboDKHandler] 🧹 Cleared all taught positions.")

    def has_taught_positions(self):
        return len(self.taught_positions) > 0

    def teach_object_pose(self, pose, angle_deg=0.0):
        """Teach a pose with orientation angle"""
        full_pose = self._pose_with_rotation(pose, angle_deg)
        self.taught_object_poses.append(full_pose)
        print(f"[RoboDKHandler] 📌 Object pose taught at {pose.Pos()} with angle {angle_deg}°")

    def simulate_object_poses(self):
        for pose in self.taught_object_poses:
            full_pose = self._safe_target_pose(pose)
            joints = self.robot.SolveIK(full_pose)
            if joints is not None and joints.size(1) != 0:
                self.robot.MoveJ(joints)

    def create_point(self, name, pose):
        """Create a target point in RoboDK at the given pose"""
        reference_frame = self.robot.Frame()
        if not reference_frame.Valid():
            print("⚠️ Robot frame invalid. Using station root.")
            reference_frame = self.RDK.Item('', robolink.ITEM_TYPE_FRAME)

        target = self.RDK.AddTarget(name, self.robot, reference_frame)
        if target.Valid():
            target.setPose(pose)
            print(f"[RoboDKHandler] 📍 Target '{name}' created at pose: {pose.Pos()}")
        else:
            print(f"[RoboDKHandler] ❌ Failed to create target '{name}'")
