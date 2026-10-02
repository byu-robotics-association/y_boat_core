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

- *(Recommended)* Install VSCode on your system. This is the preferred and supported development IDE for this project. Use other IDEs with caution. [Download Link](https://code.visualstudio.com/download?_exp_download=fb315fc982)

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
The default .env settings work right away for general development, change these variables when neccesary

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
All packages should be created inside src/nodes/

Check out the tutorials in [ROS2 Demo](https://github.com/byu-robotics-association/y_robotics_ros2_demo)

### Type Annotations
Every function must declare types for its arguments and return value (e.g. `def main(args: list[str] | None = None) -> None:`). CI checks this with Ruff on every PR; run the same check locally from the repo root with:
```bash
pip install ruff==0.16.5
ruff check src .github
```

#### Help with strong typed syntax
In VS Code, install the recommended extensions when prompted (or search `@recommended` in the Extensions view). Missing annotations are then underlined as you type. Hover over one and click its rule code to open Ruff's explanation with a before/after example.

```python
# Syntax for declaring types when defining a function
def int_to_string(parameter_name: int) -> str:
    return str(parameter_name)

# Syntax for declaring type on a variable
my_string: str = int_to_string(5) # This isn't necessary, and isn't enforced in the tests, but it's still helpful sometimes.
```

It's also good to understand that adding these strong type declarations do not change the behavior of the code, it simply makes the code more readable and makes development easier.

### Run Tests Before Opening a PR
Every PR runs CI checks: the type annotation check above, a build of the Docker image and workspace, and the tests for each package the PR changes. Run the same checks locally with:
```bash
./scripts/test.sh boat_perception
```
Name the package(s) you changed; packages that depend on them are tested too. Run `./scripts/test.sh` with no arguments to test everything. The first run builds the Docker image and takes a few minutes; later runs are quick. See `./scripts/test.sh -h` for options.

#### Sync with Git Changes
The following command will sync your local environment with origin/main
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

