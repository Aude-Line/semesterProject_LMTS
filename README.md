# semesterProject_LMTS

## Intro

TODO: Add a short project overview.

## WSL Setup

This project is developed in WSL2 on Ubuntu 22.04.

TODO: install WSL and mode miroir

### 1) Install a dedicated distro for this project (PowerShell)

```powershell
wsl --install Ubuntu-22.04 --name Ubuntu-22.04-semesterProject --version 2 --web-download
```

During first launch, create your Linux user and set a password.

### 2) Launch the project distro (PowerShell)

```powershell
wsl -d Ubuntu-22.04-semesterProject
```

### 3) Verify WSL version (PowerShell)

```powershell
wsl --list --verbose
```
Expected: the distro used for the project is on version `2`.

## Structure of This Repo

Main folders:

- `fp_bridge`: bridge code to connect to the robot ROS node (Git submodule)
- `esp`: ESP code (Git submodule)

Clone the project with all submodules (including submodules inside submodules):

```bash
cd ~
git clone --recurse-submodules https://github.com/Aude-Line/semesterProject_LMTS.git
cd semesterProject_LMTS
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

Go to the repository root at any time:

```bash
cd ~/semesterProject_LMTS
```

## Bridge

Reference guide:
https://docs.ros.org/en/humble/How-To-Guides/Using-ros1_bridge-Jammy-upstream.html

### 1) Install ROS1 core packages on Ubuntu 22.04 (Jammy)

```bash
sudo apt update
sudo apt install -y ros-core-dev
```

Note: on Jammy with this setup, `/opt/ros/noetic` is not present. Do not run `source /opt/ros/noetic/setup.bash`.

### 2) Install build tools (required for C++)

```bash
sudo apt update
sudo apt install -y build-essential g++ cmake git
```

### 4) Build `ros1_ws`

```bash
cd ~/semesterProject_LMTS/fp_bridge/ros1_ws
catkin_make
```

Expected result: CMake config completes and `make` runs without `No CMAKE_CXX_COMPILER could be found`.

### 5) Download ROS2 humble from sources, compatiblel with ros1
TODO: copy log file

### 6) Build ROS2 humble
open a new wsl terminal and type
```bash
cd ~/ros2_humble
colcon build --symlink-install --packages-skip-build-finished
```

as the build is really long and some library takes too much memory for WSL, if the build stops or is stuck try with this to build the problematics libraries

```bash
MAKEFLAGS="-j1" colcon build --symlink-install --packages-skip-build-finished --executor sequential
```

### Build the bridge


### Run steps for bridge

TODO: Add exact runtime commands for your bridge nodes.

## ESP

TODO: Add build steps for `esp`.
TODO: Add run steps for `esp`.

## Run Code

TODO: Add execution steps for bridge and ESP.
