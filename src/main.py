import time
import argparse
from kdtree import KDTree
from input import ObjReader
from average_block_colors import color_block_pairs
from render import MinecraftWorldEditor, VoxelRenderer
from voxelize import VoxelizerMinecraft, VoxelizerWithoutMinecraft

def main(model_path, voxel_size, world_path, build_location):
    """
    Reads input data, builds KD tree if necessary, voxelizes, and renders
    
    Args:
    - model_path (str): path to 3D model
    - voxel_size (float): sidelength of each voxel (smaller = more detail)
    - world_path (str): path to minecraft world
    - build_location (list): minecraft world coordinates at which to build the structure
    """
    try:
        build_in_minecraft = True if world_path and build_location else False

        start_time = time.time()

        print("preprocessing")

        model = ObjReader(model_path)
        model.read_file()

        if build_in_minecraft:
            kdtree = KDTree(list(color_block_pairs.keys()))
            voxelizer = VoxelizerMinecraft(model, voxel_size, kdtree)
        else:
            voxelizer = VoxelizerWithoutMinecraft(model, voxel_size)

        print("voxelizing")
        voxelizer.voxelize()

        print(f"Time elapsed: {time.time() - start_time}")

        if build_in_minecraft:
            MinecraftWorldEditor(world_path).build_structure(voxelizer.block_grid, build_location)
        else:
            VoxelRenderer.render_without_minecraft_blocks(voxelizer.voxel_grid, voxelizer.color_grid)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voxelizes a 3D model and either builds it in Minecraft or renders it with PyVista")
    parser.add_argument("model_path", type=str, help="Path to the 3D model (ex. your_model.obj)")
    parser.add_argument("voxel_size", type=float, help="Side length of each voxel (smaller means higher resolution and thus more voxels)")
    parser.add_argument("--world-path", type=str, help="Path to the Minecraft world")
    parser.add_argument("--build-location", type=str, help="Coordinates at which to build model in the form: \"(x,y,z)\" (quotes must be included)")
    args = parser.parse_args()

    if args.voxel_size <= 0:
        raise ValueError("Voxel size must be > 0")

    build_location = None
    if args.build_location:
        try:
            x, y, z = map(int, args.build_location[1:-1].split(","))
            build_location = [x, y, z]
        except ValueError:
            raise ValueError("Build location must be in the form \"(x,y,z)\" (quotes must be included) where x, y, and z are all ints")

    main(args.model_path, args.voxel_size, args.world_path, build_location)