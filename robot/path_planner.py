from robodk.robomath import transl

class PathPlanner:
    def __init__(self):
        self.z_pick = 100     # mm above surface
        self.z_place = 150    # mm above surface
        self.z_move = 200     # mm travel height

    def generate_path(self, operation, poses):
        """
        Generate robot path based on operation type.
        `poses` should be a list of Mat transforms (robot coordinates)
        """
        path = []
        if not isinstance(poses, list):
            poses = [poses]

        for pose in poses:
            if operation.lower() == "pick":
                path.append(pose * transl(0, 0, self.z_pick))  # approach
                path.append(pose)  # pick
                path.append(pose * transl(0, 0, self.z_pick))  # retreat
            elif operation.lower() == "place":
                path.append(pose * transl(0, 0, self.z_place))  # approach
                path.append(pose)  # place
                path.append(pose * transl(0, 0, self.z_place))  # retreat
            elif operation.lower() == "move":
                path.append(pose * transl(0, 0, self.z_move))
            else:
                raise ValueError(f"[PathPlanner] Unknown operation: {operation}")

        return path