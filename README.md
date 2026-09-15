# y_boat_core
This is the official BYU Robotics Association Boat Software, including all firmware needed for every microcontroller and 
## Getting Started with Development
### Prereqs
- Install docker on your system (follow instructions online for Windows, MacOS, or Linux)
```bash
git clone https://github.com/BYU-Y-Robotics/y_boat_core.git
cd y_boat_core
``` 

Copy the .env-example file into .env
```bash
cp .env-example .env
```
Update this .env file with the appropriate configuration for your environment

To test that everything is set up correctly, build and run the container with:
```bash
docker compose build dev
docker compose run --rm dev 
```
This opens the container with a terminal for you to interact with the docker container.

Run this to test every change you make.

All packages should be created inside src/nodes/
