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
- `CAD_gripper`: gripper CAD files (Git submodule)

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
### Bridge intro
humble with upstream to be able to use bool patch -> less stable
the bridge code was also modified to be able to use personal class tables (Joints[])

The fp library was modified to generate readable ROS1 msg and srv, and a ROS2 side was implemented, with custom mapping rules

with custom mapping rules the bridge needs to be recompiled, but as I modified it it needed to be recompiled anyway

Reference guides:
https://docs.ros.org/en/humble/How-To-Guides/Using-ros1_bridge-Jammy-upstream.html

https://docs.ros.org/en/humble/p/ros1_bridge/doc/index.html

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

as the build is really long (around 2h on my computer) and some library takes too much memory for WSL, if the build stops or is stuck try with this to build the problematics libraries

```bash
MAKEFLAGS="-j1" colcon build --symlink-install --packages-skip-build-finished --executor sequential
```

### Build ros2 ws
in a new shell
```bash
cd ~/semesterProject_LMTS/fp_bridge/ros2_ws

source ~/ros2_humble/install/setup.bash

colcon build
```

### Build the bridge
in a clean shell
Before building the bridge, install the ROS1 Python modules it imports:

```bash
sudo apt update
sudo apt install -y python3-rosmsg python3-roslib python3-rospkg python3-catkin-pkg python3-genpy
```

Then build the bridge:

```bash
cd ~/semesterProject_LMTS/fp_bridge/bridge_ws

source ~/semesterProject_LMTS/fp_bridge/ros1_ws/devel/setup.bash

source ~/ros2_humble/install/setup.bash

source /home/fleur/semesterProject_LMTS/fp_bridge/ros2_ws/install/setup.bash

MAKEFLAGS="-j1" colcon build --packages-select ros1_bridge --cmake-force-configure --event-handlers console_direct+
```

### Offline check for `fp_core_msgs`

Even if you do not have access to the ROS 1 robot, you can still inspect the bridge pair list and filter it to `fp_core_msgs` to check if the bridge compilation was sucessful:

```bash
source ~/semesterProject_LMTS/fp_bridge/ros1_ws/devel/setup.bash
source ~/ros2_humble/install/local_setup.bash
source ~/semesterProject_LMTS/fp_bridge/ros2_ws/install/local_setup.bash
source ~/semesterProject_LMTS/fp_bridge/bridge_ws/install/local_setup.bash

ros2 run ros1_bridge dynamic_bridge --print-pairs | grep fp_core_msgs
```

This only shows supported message pairs. It does not require the bridge to connect to the robot.

### Run steps for bridge

See the runtime commands in the Run Code section below.

## ESP

TODO: Add build steps for `esp`.
TODO: Add run steps for `esp`.

## Run Code

### Bridge runtime

In a new shell, source the same workspaces and point the bridge to the ROS 1 master:

```bash
cd

source ~/semesterProject_LMTS/fp_bridge/ros1_ws/devel/setup.bash
source ~/ros2_humble/install/local_setup.bash
source ~/semesterProject_LMTS/fp_bridge/ros2_ws/install/local_setup.bash
source ~/semesterProject_LMTS/fp_bridge/bridge_ws/install/local_setup.bash

export ROS_MASTER_URI=http://10.0.0.203:11311
export ROS_IP=172.23.10.4

ros2 run ros1_bridge dynamic_bridge --bridge-all-topics
```

If you see `Failed to contact master`, check that `ROS_MASTER_URI` points to the machine running ROS 1 and that `ROS_IP` matches this WSL instance.

### ESP runtime

TODO: Add execution steps for ESP.
