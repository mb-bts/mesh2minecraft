# mesh2minecraft
This project takes a 3D model as input (OBJ file) and converts it into cubes (i.e. voxels), which can then be either visualized directly or imported into a Minecraft world. The process of converting the model to voxels (i.e. voxelization) is accomplished by performing intersection tests between the input model’s triangles and the candidate voxels (spots where a voxel might be placed) using the Separating Axis Theorem. When it’s desired to import the model into Minecraft, a kd-tree is used to quickly associate any given color with the Minecraft block that resembles it the closest. For additional information, see the [descriptions](#file-specific-explanations) I’ve written for each Python file.

***IMPORTANT NOTE 1***: Only compatible with OBJ files that contain vertex colors (most don’t since this contradicts the traditional/formal OBJ standards).

***IMPORTANT NOTE 2***: Only tested with Minecraft 1.13.

## Installation and Setup
```
git clone https://github.com/mb-bts/mesh2minecraft.git
cd mesh2minecraft
pip install -r requirements.txt
```

## Usage
To use without Minecraft, just specify the OBJ file’s name/path, and provide a number which determines the sidelength of each voxel (lower sidelength means there will be more voxels).
```
python src/main.py test_models/cow.obj 0.05
```
<p align="center"><img src="/images/voxelized_cow.png" alt="Image of voxelized cow" style="width:50%;"></p>

To use with Minecraft, include the path to the world and the coordinates at which to build the structure. Be sure to adapt the world path if necessary to suit your system (I used a Mac), replace YOUR_WORLD_NAME with your world's name, and adjust the build location if desired. 
```
python src/main.py test_models/cow.obj 0.05 --world-path “~/Library/Application Support/minecraft/YOUR_WORLD_NAME” --build-location “(0, 4, 0)”
```
<p align="center"><img src="/images/minecraft_cow.png" alt="Image of voxelized cow" style="width:50%;"></p>

## File-Specific Explanations

**[`main.py`](src/main.py)** is responsible for taking input from the command line (model file, voxel size, etc.) and handling any associated errors, as well as calling the major methods to orchestrate the entire process and tie everything together.

**[`input.py`](src/input.py)** handles file reading and parsing. There’s a base class called `FileReader` and a subclass called `ObjReader`. Part of the reason for splitting this file into multiple classes has to do with error handling. No matter what type of file is being read, the file will need to be opened, meaning errors like incorrect file names or insufficient permissions might occur. For this reason, all error handling is handled in `FileReader`. The other motivation for having multiple classes is that if it’s ever desired to add functionality for reading other types of files (besides OBJ), it will be fast and easy to do this in a concise and maintainable fashion.

**[`kdtree.py`](src/kdtree.py)** contains a simple kd-tree implementation which includes the `get_nearest_point` method that takes an input point and returns the nearest point it can find in the kd-tree. This is useful because if we build a kd-tree containing the average color of each Minecraft block, then given a voxel’s color as input, `get_nearest_point` can effectively determine which Minecraft block matches the voxel’s color the best. Note the use of abstraction in that `get_nearest_point_helper` does most of the work thus simplifying the public-facing `get_nearest_point` such that it only requires one parameter to be passed.

**[`voxelizer.py`](src/voxelizer.py)** is perhaps the most important file in this project. It’s responsible for voxelizing the input model, and it does so differently depending on whether it’s desired that the final rendering be in Minecraft or PyVista. This is accomplished by detailing most of the logic in the `VoxelizerBase` class, and then allowing subclasses `VoxelizerMinecraft` and `VoxelizerWithoutMinecraft` to inherit from `VoxelizerBase` and provide their own specific functionality on top of this.

`VoxelizerBase` works by iterating over each triangle in the model, finding each triangle’s bounding box, and performing intersection tests with each voxel overlapping the given triangle’s bounding box. The `_populate_grids` method fills in the `voxel_grid` (which contains a boolean for each voxel (dictating its presence)) accordingly depending on whether the intersection occurred or not.

The subclasses both override `_populate_grids` to provide specialized functionality. In the case of `VoxelizerMinecraft`, the `block_grid` is populated with the Minecraft block names possessing the average color most similar to that of the voxel color. It accomplishes this with a kd-tree which of course is only initiated in the `VoxelizerMinecraft` subclass. As for `VoxelizerWithoutMinecraft`, `_populate_grids` simply populates the `color_grid` with the desired RGB values for each voxel.

**[`render.py`](src/render.py)** contains classes `MinecraftWorldEditor` and `VoxelRenderer`, the former of which builds the voxelization by editing the Minecraft world directly using PyAnvilEditor, while the latter simply renders it using PyVista with regular colored voxels as opposed to Minecraft blocks.

**[`voxel_triangle_intersection.py`](src/voxel_triangle_intersection.py)** is based on [this](https://gist.github.com/zvonicek/fe73ba9903f49d57314cf7e8e0f05dcf) program which itself seems to have been based on a [thread](https://www.gamedev.net/forums/topic/534655-aabb-triangleplane-intersection--distance-to-plane-is-incorrect-i-have-solved-it/) regarding pages 169-172 of “Real-Time Collision Detection” by Christer Ericson. My version builds upon the original program with a number of improvements:
1. **Removed NumPy:** The original used NumPy throughout for vector operations, but regular Python code turned out to be faster in my testing. I’m unsure of the exact reason but I imagine it was because NumPy’s overhead outweighed its benefits since the vectors (NumPy arrays) in question were only of length 3.
2. **Simplified arithmetic:** In my case, it was only necessary to perform intersection tests on voxels (cubes) as opposed to arbitrarily-sized boxes as the original code had been designed for. This meant I was able to simplify the projection radius computations. For example, something like `r = box_length_x * abs(a) + box_length_y * abs(b)` became `r = box_length * (abs(a) + abs(b))`. Note that I tried `r = box_length * (abs(a+b))` but this was slower for a reason that’s still unclear.
3. **Reduced redundancy:** There were places where something like `abs(a)` was calculated twice in the original so I replaced every instance of something like `abs(a)` with something like `abs_a = abs(a)`.
4. **Added early exit opportunity:** If any of a triangle’s points are within a voxel then there must be an intersection, and since this can be checked quickly and easily, and occurs fairly often, I added this check and put it at the start of the method.

All together, these changes made the code much more efficient, but there’s always room for improvement. For example, a potential future change might be to calculate the projections exactly as suggested in Ericson’s book, where he’s able to compute only two thirds of the projections that I do (all while achieving the same results).

**[`average_block_colors.py`](src/average_block_colors.py)** contains the dictionary which pairs the names of various Minecraft blocks with their average color. I built this dictionary automatically with a function that iterated through Minecraft assets. However, I did some manual work to improve the list since not all the assets were blocks (some were plants, doors, beds, etc.) and some blocks were not “persistent” (ex. ice melts and sand falls). It is for this reason that I’ve excluded the code that collected the initial list of potential “blocks” and found their average colors, along with the fact that it’s inefficient and unnecessary to recalculate this for each voxelization. However, a potential future improvement would certainly be to automate this entire process since then when a user updates their Minecraft game, the assets folder would then be populated with any new blocks enabling them to be included in the build.
