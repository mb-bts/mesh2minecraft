# """
# improvements I've done:
# - remove np
# - set to vars to avoid frequent indexing
# - x * abs(y) + x * abs(z) became x * (abs(y) + abs(z))
# - added check if any vertex in voxel at start
# - precomputing abs calls

# further improvements:
# - changes in book so only find two projections for each axis
# - 
# """

class TriangleVoxelIntersection:
    """Class for detecting intersections between triangles and voxels"""

    def __init__(self, triangle, voxel_center, voxel_size):
        """
        Initializes TriangleVoxelIntersection

        Args:
        - triangle (list): contains each of the triangle's three vertices 
        - voxel_center (list): coordinates of the voxel's center
        - voxel_size (float): sidelength of voxel
        """
        self.triangle = triangle
        self.voxel_center = voxel_center
        self.voxel_size = voxel_size

    def intersects(self):
        """
        Performs a triangle-voxel intersection test using the separating axis theorem
        
        Returns:
        - bool: True if an intersection occurs, False otherwise
        """
        v0, v1, v2 = self.triangle
        cx, cy, cz = self.voxel_center

        # translate triangle
        v0_x, v0_y, v0_z = v0[0] - cx, v0[1] - cy, v0[2] - cz
        v1_x, v1_y, v1_z = v1[0] - cx, v1[1] - cy, v1[2] - cz
        v2_x, v2_y, v2_z = v2[0] - cx, v2[1] - cy, v2[2] - cz

        # early exit if triangle's point is in voxel, since this means there must be an intersection
        if self._point_in_voxel(v0_x, v0_y, v0_z): return True
        if self._point_in_voxel(v1_x, v1_y, v1_z): return True
        if self._point_in_voxel(v2_x, v2_y, v2_z): return True

        # get triangle edges
        e0_x, e0_y, e0_z = [v1_x - v0_x, v1_y - v0_y, v1_z - v0_z]
        e1_x, e1_y, e1_z = [v2_x - v1_x, v2_y - v1_y, v2_z - v1_z]
        e2_x, e2_y, e2_z = [v0_x - v2_x, v0_y - v2_y, v0_z - v2_z]

        # calculate projections
        p0 = v0_y * e0_y - v0_z * e0_z
        p1 = v1_y * e0_y - v1_z * e0_z
        p2 = v2_y * e0_y - v2_z * e0_z
        abs_e0_z = abs(e0_z)
        abs_e0_y = abs(e0_y)
        r = self.voxel_size * (abs_e0_z + abs_e0_y) # calculate projection radius
        if self._is_separating_axis(p0, p1, p2, r): return False

        # calculate projections
        p0 = v0_z * e1_y - v0_y * e1_z
        p1 = v1_z * e1_y - v1_y * e1_z
        p2 = v2_z * e1_y - v2_y * e1_z
        abs_e1_z = abs(e1_z)
        abs_e1_y = abs(e1_y)
        r = self.voxel_size * (abs_e1_z + abs_e1_y) # calculate projection radius
        if self._is_separating_axis(p0, p1, p2, r): return False

        # calculate projections
        p0 = v0_z * e2_y - v0_y * e2_z
        p1 = v1_z * e2_y - v1_y * e2_z
        p2 = v2_z * e2_y - v2_y * e2_z
        abs_e2_z = abs(e2_z)
        abs_e2_y = abs(e2_y)
        r = self.voxel_size * (abs_e2_z + abs_e2_y) # calculate projection radius
        if self._is_separating_axis(p0, p1, p2, r): return False

        # calculate projections
        p0 = v0_x * e0_z - v0_z * e0_x
        p1 = v1_x * e0_z - v1_z * e0_x
        p2 = v2_x * e0_z - v2_z * e0_x
        abs_e0_x = abs(e0_x)
        r = self.voxel_size * (abs_e0_z + abs_e0_x) # calculate projection radius
        if self._is_separating_axis(p0, p1, p2, r): return False

        # calculate projections
        p0 = v0_x * e1_z - v0_z * e1_x
        p1 = v1_x * e1_z - v1_z * e1_x
        p2 = v2_x * e1_z - v2_z * e1_x
        abs_e1_x = abs(e1_x) 
        r = self.voxel_size * (abs_e1_z + abs_e1_x) # calculate projection radius
        if self._is_separating_axis(p0, p1, p2, r): return False

        # calculate projections
        p0 = v0_x * e2_z - v0_z * e2_x
        p1 = v1_x * e2_z - v1_z * e2_x
        p2 = v2_x * e2_z - v2_z * e2_x
        abs_e2_x = abs(e2_x)
        r = self.voxel_size * (abs_e2_z + abs_e2_x) # calculate projection radius
        if self._is_separating_axis(p0, p1, p2, r): return False

        # calculate projections
        p0 = v0_y * e0_x - v0_x * e0_y
        p1 = v1_y * e0_x - v1_x * e0_y
        p2 = v2_y * e0_x - v2_x * e0_y
        r = self.voxel_size * (abs_e0_y + abs_e0_x) # calculate projection radius
        if self._is_separating_axis(p0, p1, p2, r): return False

        # calculate projections
        p0 = v0_y * e1_x - v0_x * e1_y
        p1 = v1_y * e1_x - v1_x * e1_y
        p2 = v2_y * e1_x - v2_x * e1_y
        r = self.voxel_size * (abs_e1_y + abs_e1_x) # calculate projection radius
        if self._is_separating_axis(p0, p1, p2, r): return False

        # calculate projections
        p0 = v0_y * e2_x - v0_x * e2_y
        p1 = v1_y * e2_x - v1_x * e2_y
        p2 = v2_y * e2_x - v2_x * e2_y
        r = self.voxel_size * (abs_e2_y + abs_e2_x) # calculate projection radius
        if self._is_separating_axis(p0, p1, p2, r): return False

        # exit if triangle's bounding box doesn't overlap with voxel
        if max(v0_x, v1_x, v2_x) < -self.voxel_size or min(v0_x, v1_x, v2_x) > self.voxel_size:
            return False
        if max(v0_y, v1_y, v2_y) < -self.voxel_size or min(v0_y, v1_y, v2_y) > self.voxel_size:
            return False
        if max(v0_z, v1_z, v2_z) < -self.voxel_size or min(v0_z, v1_z, v2_z) > self.voxel_size:
            return False

        # exit if triangle's plane doesn't intersect with voxel
        plane_normal = [e0_y * e1_z - e0_z * e1_y, e0_x * e1_z - e0_z * e1_x, e0_x * e1_y - e0_y * e1_x]
        plane_distance = plane_normal[0] * v0_x + plane_normal[1] * v0_y + plane_normal[2] * v0_z
        r = self.voxel_size * (abs(plane_normal[0]) + abs(plane_normal[1]) + abs(plane_normal[2]))
        if plane_distance > r:
            return False

        return True
    
    def _point_in_voxel(self, x, y, z):
        """
        Checks if the point with the given XYZ values is within the voxel
        
        Args:
        - x (float): x coordinate of point
        - y (float): y coordinate of point
        - z (float): z coordinate of point

        Returns:
        - bool: True if the point is in the voxel, False otherwise
        """
        return (
            -self.voxel_size <= x <= self.voxel_size and 
            -self.voxel_size <= y <= self.voxel_size and 
            -self.voxel_size <= z <= self.voxel_size
        )

    @staticmethod
    def _is_separating_axis(p0, p1, p2, r):
        """
        Checks whether axis is separating axis

        Args:
        - p0 (float): distance from v0 projection to origin
        - p1 (float): distance from v1 projection to origin
        - p2 (float): distance from v2 projection to origin

        Returns:
        - bool: True if axis is separating axis, False otherwise
        """
        return max(-max(p0, p1, p2), min(p0, p1, p2)) > r 