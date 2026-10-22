# boat_image_processing

This package is responsible for handling the YOLO model and image processing as part of perception for the robot.

## Package Development

The package uses this layout:

```text
boat_image_processing/
    boat_image_processing/       Python node modules
    launch/                 ROS 2 launch configurations
    setup.py                Package metadata and executables
    package.xml             ROS 2 dependencies
```

### Add a Python Node

1. Create the node module in `boat_image_processing/` and define a `main()` function. For example:

   ```text
   src/boat_image_processing/boat_image_processing/new_node.py
   ```

2. Register the node as a console script in `setup.py`:

   ```python
   'console_scripts': [
        'object_detector = boat_image_processing.object_detector:main',
        'new_node = boat_image_processing.new_node:main',
   ],
   ```

3. Add the node to a launch file in `launch/`:

   ```python
   Node(
       package='boat_image_processing',
       executable='new_node',
       name='new_node',
       output='screen',
   ),
   ```

   The `executable` value must match the console script name in `setup.py`.

The `launch/` directory can contain multiple launch configurations, such as:

```text
launch/
    boat_image_processing.launch.py
    cameras.launch.py
    simulation.launch.py
```

The existing `setup.py` configuration installs every `*.launch.py` file in this directory, so new launch files do not need additional registration.

### Build and Run

Rebuild and source the workspace after adding a node, changing `setup.py`, changing `package.xml`, or adding a launch file:

```bash
colcon build --packages-select boat_image_processing --symlink-install
source install/setup.bash
```

With `--symlink-install`, edits inside an existing Python node usually do not require a rebuild. Rebuild when package metadata, console scripts, dependencies, package structure, or launch files change.

Run the main perception launch file with:

```bash
ros2 launch boat_image_processing boat_image_processing.launch.py
```

The repository also includes a VS Code debug configuration at `.vscode/launch.json`. Select `ROS 2: Debug boat_image_processing` from Run and Debug to debug the launch file and its nodes. Rebuild the package before debugging after changing launch-related files.
