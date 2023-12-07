import numpy as np
import pyvista as pv
from pyanvileditor import world

class MinecraftWorldEditor:
    """Class that displays voxelization results by directly editing a minecraft world"""

    def __init__(self, world_path):
        """
        Initializes MinecraftWorldEditor

        Args:
        - world_path (str): path to minecraft world file
        """
        self.world_path = world_path

    def build_structure(self, block_grid, build_location):
        """
        Builds the structure defined by the given block grid

        Args:
        - block_grid (np.ndarray): 3D grid of block names 
        - build_location (tuple): the XYZ coords at which to build the structure
        """
        with world.World(self.world_path) as minecraft_world:
            for x in range(block_grid.shape[0]):
                for y in range(block_grid.shape[1]):
                    for z in range(block_grid.shape[2]):
                        if block_grid[x, y, z]:
                            block = minecraft_world.get_block((x + build_location[0], y + build_location[1], z + build_location[2]))
                            block.set_state(world.BlockState(f"minecraft:{block_grid[x, y, z]}", {}))

class VoxelRenderer:
    """Class that renders voxels without minecraft (using PyVista)"""

    @staticmethod
    def render_without_minecraft_blocks(voxel_grid, color_grid):
        """
        Renders voxels with PyVista

        Args:
        - voxel_grid (np.ndarray): 3D bool array indicating voxel presence
        - color_grid (np.ndarray): 3D array containing RGB values for each voxel
        """
        points = []
        colors = []
        for x in range(voxel_grid.shape[0]):
            for y in range(voxel_grid.shape[1]):
                for z in range(voxel_grid.shape[2]):
                    if voxel_grid[x, y, z]:
                        points.extend((
                            (x, y, z),
                            (x + 1, y, z),
                            (x + 1, y + 1, z),
                            (x, y + 1, z),
                            (x, y, z + 1),
                            (x + 1, y, z + 1),
                            (x + 1, y + 1, z + 1),
                            (x, y + 1, z + 1)
                        ))
                        colors.append(color_grid[x, y, z])

        points = np.array(points, dtype=np.float32)
        point_indices = np.array(range(len(points)))

        grid = pv.UnstructuredGrid({pv.CellType.HEXAHEDRON: point_indices}, points)
        grid.cell_data["colors"] = colors

        plotter = pv.Plotter()
        plotter.add_mesh(grid, scalars="colors", rgb=True) 
        plotter.show()