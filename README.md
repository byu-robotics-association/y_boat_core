# y_boat_core
This is the official BYU Robotics Association Boat Software, including all firmware needed for every microcontroller and main compute modules onboard.
## Getting Started with Development

### Prereqs
- Install Git on your system. Download for [Windows](https://git-scm.com/install/windows), [MacOS](https://git-scm.com/install/mac), [Linux](https://git-scm.com/install/linux)

- Install Docker Desktop on your system. Download for [Windows](https://docs.docker.com/desktop/setup/install/windows-install/), [MacOS](https://docs.docker.com/desktop/setup/install/mac-install/), [Linux](https://docs.docker.com/desktop/setup/install/linux/)

> Windows Users, Ensure WSL is installed on your computer. Run this command in a powershell terminal
>```powershell
>wsl --install
>```

- *(Recommended)* Install VS Code on your system. This is the preferred and supported development IDE for this project. Use other IDEs with caution. [Download Link](https://code.visualstudio.com/download?_exp_download=fb315fc982)

### Docker setup
On Mac and Windows, open the docker desktop app. You will need to open this app anytime you want to run the scripts

> On Linux, ensure you have added your user to the docker group, you only run this one time. You need to log out and log back in for these settings to apply
>```bash
>sudo usermod -aG docker $USER
>```
### Clone Repo
On Windows, open a WSL terminal (this should have been downloaded with Docker Desktop). On Mac and Linux, simply open a terminal

Navigate to the folder you want to have the project in:
```bash
git clone https://github.com/BYU-Y-Robotics/y_boat_core.git
cd y_boat_core
code .
``` 
> Mac Users - if *code .* fails, you need to install the code command to your PATH. Open VS Code, press Cmd + Shift + P, search and run *Shell Command: Install 'code' command in PATH*. Restart your terminal and try to run the command again


### Copy Environment Configuration File
Copy the .env-example file into .env
```bash
cp .env-example .env
```
The default .env settings work right away for general development, change these variables when necessary.

### Development Container
For interactive development in VS Code, install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

Make sure Docker is running before starting the development container.

Open the repository in VS Code. Click the remote window button in the lower-left corner of the VS Code window, then select **Reopen in Container**.

After the container is ready, open a terminal in VS Code and verify that ROS 2 is available:

```bash
ros2
```

The container performs an initial build automatically. Run this command manually after making package changes from within the container.

```bash
colcon build --packages-select <package_name> --symlink-install
source install/setup.bash
```

For VS Code-based development, use the Dev Container workflow above. The `scripts/run.sh` workflow below is also available for terminal-based development, runtime testing, or running the project on the boat.

### Make the Scripts Executable
```bash
chmod +x ./scripts/run.sh
```

### Build and Run the Container
To check that everything is set up correctly, build and run the container with:
```bash
./scripts/run.sh -i -p
```
The -i parameter makes it interactive, -p checks to make sure the docker image is updated and pulled correctly

This opens the container and runs the ROS2 startup, you should now have an interactive terminal inside the docker container

Run this command, if it does not give you an error, you have done everything correctly!
```bash
ros2
```

### Development
All packages should be created inside `src/nodes/`

Check out the tutorials in [ROS2 Demo](https://github.com/byu-robotics-association/y_robotics_ros2_demo)

For documentation on a specific package, take a look at its package README.
| Package | Description | Documentation |
|---|---|---|
| `boat_perception` | Environment perception system | [`README.md`](src/nodes/boat_perception/README.md) |

### Build a Package

```bash
colcon build --packages-select <package_name> --symlink-install
source install/setup.bash
```

### Run a Package

```bash
ros2 launch <package_name> <launch_file>.launch.py
```

For package-specific instructions, see that package's README.

#### Sync with Git Changes
The following command will sync your local environment with origin/main

Open a shell inside the container:
```bash
docker exec -it boat_dev bash
```

ROS 2 and the workspace overlay are sourced automatically in interactive shells. If you
ever need to do it by hand:
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source /workspace/install/setup.bash    # only exists after a build
```

## ROS 2 Packages

### 1. Create a Package
Inside the container:
```bash
cd /workspace/src/nodes      # or another directory under /workspace/src
ros2 pkg create --build-type ament_python <package_name> --dependencies rclpy
```

### 2. Build a Package
Always build from `/workspace`, never from `/workspace/src`. Building from `src/` creates a
second, competing `install/` overlay and it becomes ambiguous which one you have sourced.
```bash
cd /workspace
colcon build --symlink-install --packages-select <package_name>
```

### 3. Run a Node
```bash
source /workspace/install/setup.bash
ros2 run <package_name> <executable_name>
```

Example with the included perception package:
```bash
cd /workspace
colcon build --symlink-install --packages-select boat_perception
source /workspace/install/setup.bash
ros2 run boat_perception lidar_processor
```

## Connecting to the BlueBoat Simulator
`boat_control` drives the simulated boat over MAVROS. Note the executable is
`drive_test`, not `sim_node`:
```bash
cd /workspace
colcon build --symlink-install --packages-select boat_control
source /workspace/install/setup.bash
ros2 run boat_control drive_test
```

Requirements:
- The simulator must already be running and publishing MAVROS topics
  (`/mavros/state`, `/mavros/local_position/odom`).
- `ROS_DOMAIN_ID` must match between this container and the simulator. Both default
  to `10` via `.env`.
- This image ships `ros-$ROS_DISTRO-mavros`. That matters: without `mavros_msgs`,
  `sim_node.py` silently falls back to publishing `geometry_msgs/Twist` on
  `/mavros/setpoint_velocity/cmd_vel_unstamped`, which ArduPilot interprets in the
  **world ENU frame** — the boat then drives in a fixed compass direction regardless of
  its heading. With MAVROS present it uses `/mavros/setpoint_raw/local` with
  `FRAME_BODY_NED`, which is true body-frame control.

A successful run prints a drive-test summary and reports several metres of travel.

## Sync with Changes
```bash
git fetch
git pull origin main
```

If you want to sync with a different branch run
```bash
git fetch
git pull origin <branch-name>
```

### Runtime Commands
```bash
./scripts/run.sh
```
This is the command to run on the boat to start everything at once. It doesn't open the terminal or pull the latest docker image

