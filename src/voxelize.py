import numpy as np
from average_block_colors import color_block_pairs
from voxel_triangle_intersection import TriangleVoxelIntersection

class VoxelizerBase:
    """Base class for voxelizer"""

    def __init__(self, model, voxel_size):
        """
        Initializes VoxelizerBase

        Args:
        - model (ObjReader): contains parsed data from input file (vertices, faces, colors)
        - voxel_size (float): the desired sidelength for the voxels (lower = higher detail)
        """
        self.vertices = model.vertices
        self.faces = model.faces
        self.colors = model.colors
        self.voxel_size = voxel_size
        self.grid_min_corner = None
        self.grid_max_corner = None
        self.voxel_grid = None
        self.color_grid = None
        self.block_grid = None

    def grid_init(self):
        """Calculates grid dimensions and initializes grids for the voxels, voxel colors, and minecraft block names"""
        self.grid_min_corner, self.grid_max_corner = self.get_bounding_voxels(self.vertices) 
        grid_size = [self.grid_max_corner[i] - self.grid_min_corner[i] + 1 for i in range(3)] 

        self.voxel_grid = np.zeros(grid_size, dtype=bool) # stores bool indicating whether voxel present
        self.color_grid = np.zeros(grid_size + [3,], dtype=np.uint8) # RGB value for each voxel
        self.block_grid = np.empty(grid_size, dtype=object) # minecraft block name for each voxel

    def get_face_colors(self):
        """
        Gets each triangle's color by finding the average of each of the three vertices
        
        Returns:
        - face_colors (list): list of lists where each nested list is a triangle's RGB color
        """
        face_colors = []
        for face in self.faces:
            c1, c2, c3 = [self.colors[i] for i in face]
            face_color = [round((sum(channel) * 255) / 3) for channel in zip(c1, c2, c3)]
            face_colors.append(face_color)
        return face_colors
    
    def get_bounding_voxels(self, vertices):
        """
        Gets the voxels that overlap with the bounding box of the vertices

        Args:
        - vertices (list): list of lists where each nested list is the the XYZ values for a vertex

        Returns:
        - min_corner (list): position of the voxel in the minimum corner of bounding voxel box
        - max_corner (list): position of the voxel in the maximum corner of bounding voxel box
        """
        # finds bounding box coordinates for the given vertices 
        min_coord = max_coord = vertices[0]
        for vertex in vertices[1:]:
            min_coord = [min(min_coord[i], vertex[i]) for i in range(len(min_coord))]
            max_coord = [max(max_coord[i], vertex[i]) for i in range(len(max_coord))]

        # converts the coordinates to voxels
        min_corner = [round(min_coord[i] / self.voxel_size) for i in range(3)]
        max_corner = [round(max_coord[i] / self.voxel_size) for i in range(3)]

        return min_corner, max_corner
    
    def voxelize(self):
        """Iterates over triangles and performs voxel-triangle intersects tests to determine where voxels are present"""
        self.grid_init()
        face_colors = self.get_face_colors()
        half_voxel_size = self.voxel_size / 2

        # for each triangle (face)
        for fi, face in enumerate(self.faces):
            triangle = [self.vertices[i] for i in face]
            min_corner, max_corner = self.get_bounding_voxels(triangle)

            # for each voxel that overlaps with the triangle's bounding box
            for x in range(min_corner[0], max_corner[0] + 1):
                for y in range(min_corner[1], max_corner[1] + 1):
                    for z in range(min_corner[2], max_corner[2] + 1):

                        # find voxel's grid indices
                        x_index = x - self.grid_min_corner[0]
                        y_index = y - self.grid_min_corner[1]
                        z_index = z - self.grid_min_corner[2]

                        # ignore voxels that have already been identified as present
                        if self.voxel_grid[x_index, y_index, z_index]: continue

                        voxel_center = [
                            x * self.voxel_size + half_voxel_size, 
                            y * self.voxel_size + half_voxel_size, 
                            z * self.voxel_size + half_voxel_size]
                        intersection_test = TriangleVoxelIntersection(triangle, voxel_center, self.voxel_size)
                        if intersection_test.intersects(): # if triangle intersects with voxel
                            # the voxel is present, so populate the grids
                            self._populate_grids(x_index, y_index, z_index, face_colors[fi]) 
    
    def _populate_grids(self, x_index, y_index, z_index, voxel_color):
        """
        Populates the grids which store the voxelization results

        Args:
        - x_index (int): x index for grids
        - y_index (int): y index for grids
        - z_index (int): z index for grids
        - voxel_color (list): RGB values specifying voxel's color
        """
        self.voxel_grid[x_index, y_index, z_index] = True
        # the remaining grid population is implemented in subclass

class VoxelizerMinecraft(VoxelizerBase):
    """Voxelizer with minecraft-specific functionality"""

    def __init__(self, model, voxel_size, kdtree):
        """
        Initializes VoxelizerMinecraft

        Args:
        - model (ObjReader): contains parsed data from input file (vertices, faces, colors)
        - voxel_size (float): the desired sidelength for the voxels (lower = higher detail)
        - kdtree (KDTree): for finding the minecraft block color closest to each voxel's color
        """
        super().__init__(model, voxel_size)
        self.kdtree = kdtree
    
    def _populate_grids(self, x_index, y_index, z_index, voxel_color):
        """
        Overrides base class method to include block_grid population

        Args:
        - x_index (int): x index for grids
        - y_index (int): y index for grids
        - z_index (int): z index for grids
        - voxel_color (list): RGB values specifying voxel's color
        """
        super()._populate_grids(x_index, y_index, z_index, voxel_color)
        # find the minecraft block which best approximates the voxel's color
        closest_color = self.kdtree.get_nearest_point(voxel_color) 
        self.block_grid[x_index, y_index, z_index] = color_block_pairs[closest_color.value]

class VoxelizerWithoutMinecraft(VoxelizerBase):
    """Voxelizer with functionality needed when not using minecraft"""

    def _populate_grids(self, x_index, y_index, z_index, voxel_color):
        """
        Overrides base class method to include color_grid population

        Args:
        - x_index (int): x index for grids
        - y_index (int): y index for grids
        - z_index (int): z index for grids
        - voxel_color (list): RGB values specifying voxel's color
        """
        super()._populate_grids(x_index, y_index, z_index, voxel_color)
        self.color_grid[x_index, y_index, z_index] = voxel_color