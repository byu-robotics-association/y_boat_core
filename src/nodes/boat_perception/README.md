# boat_perception

This package provides the foundation for the perception system. It contains nodes for reading and processing sensor data to make sense of the surrounding environment.

## Package Development

The package uses this layout:

```text
boat_perception/
    boat_perception/       Python node modules
    launch/                 ROS 2 launch configurations
    setup.py                Package metadata and executables
    package.xml             ROS 2 dependencies
```

### Add a Python Node

1. Create the node module in `boat_perception/` and define a `main()` function. For example:

   ```text
   src/nodes/boat_perception/boat_perception/new_node.py
   ```

2. Register the node as a console script in `setup.py`:

   ```python
   'console_scripts': [
       'lidar_processor = boat_perception.lidar_processor:main',
       'new_node = boat_perception.new_node:main',
   ],
   ```

3. Add the node to a launch file in `launch/`:

   ```python
   Node(
       package='boat_perception',
       executable='new_node',
       name='new_node',
       output='screen',
   ),
   ```

   The `executable` value must match the console script name in `setup.py`.

The `launch/` directory can contain multiple launch configurations, such as:

```text
launch/
    boat_perception.launch.py
    sensors.launch.py
    simulation.launch.py
```

The existing `setup.py` configuration installs every `*.launch.py` file in this directory, so new launch files do not need additional registration.

### Build and Run

Rebuild and source the workspace after adding a node, changing `setup.py`, changing `package.xml`, or adding a launch file:

```bash
colcon build --packages-select boat_perception --symlink-install
source install/setup.bash
```

With `--symlink-install`, edits inside an existing Python node usually do not require a rebuild. Rebuild when package metadata, console scripts, dependencies, package structure, or launch files change.

Run the main perception launch file with:

```bash
ros2 launch boat_perception boat_perception.launch.py
```

The repository also includes a VS Code debug configuration at `.vscode/launch.json`. Select `ROS 2: Debug boat_perception` from Run and Debug to debug the launch file and its nodes. Rebuild the package before debugging after changing launch-related files.
