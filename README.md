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
This opens the container with a terminal for you to interact with the docker container.

Run this to test every change you make.

All packages should be created inside src/nodes/

### Type Annotations
Every function must declare types for its arguments and return value (e.g. `def main(args: list[str] | None = None) -> None:`). CI checks this with Ruff on every PR; run the same check locally from the repo root with:
```bash
pip install ruff==0.16.5
ruff check src .github
```


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
