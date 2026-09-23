# y_boat_core
This is the official BYU Robotics Association Boat Software, including all firmware needed for every microcontroller and 
## Getting Started with Development
### Prereqs
- Install docker on your system (follow instructions online for Windows, MacOS, or Linux)

### Clone Repo
```bash
git clone https://github.com/BYU-Y-Robotics/y_boat_core.git
cd y_boat_core
``` 

### Copy Secrets File
Copy the .env-example file into .env
```bash
cp .env-example .env
```
Update this .env file with the appropriate configuration for your environment

### Make the Scripts executables
```bash
chmod +x ./scripts/run.sh
```

### Build and Run the Container
To test that everything is set up correctly, build and run the container with:
```bash
./scripts/run.sh
```
This opens the container and runs the ROS2 startup

For testing, run this as
```bash
./scripts/run.sh -i -p
```
The -i parameter makes it interactive, -p checks to make sure the docker image is updated and pulled correctly

Run this to test every change you make.

All packages should be created inside src/nodes/


### Sync with Changes
The following command will sync your local environment with origin/main
```bash
git fetch
git pull origin
```

If you want to sync with a different branch run
```bash
git fetch
git pull origin/your/branch/name
```
