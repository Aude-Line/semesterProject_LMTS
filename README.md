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

### Install Docker

On Ubuntu 22.04 (WSL), easiest install:

```bash
sudo apt update
sudo apt install -y docker.io
```

It is also possible to add docker to the usermd to not need to use sudo for commands, I didnt do it

### get the IP
```bash
hostname -I
```

### Run the microros agent
The agent needs to run (in it's own terminal) to allows the connection between the ESP and the computer, start the agent first (before powering or flashing the ESP).
```bash
sudo docker run -it --rm --net=host microros/micro-ros-agent:humble udp4 --port 8888 -v6
```

### Run the control file
Source humble
run python file

this will create a ros2 publisher and send on/off commands to the gripper

```bash
cd ~/semesterProject_LMTS/esp

source ~/ros2_humble/install/setup.bash

python3 gripper_ctrl.py

```

### Build and flash ESP
Check if the USB is visible on WSL
```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```
If nothing appears, bind and attach the ESP USB device from **Windows PowerShell (Run as Administrator)**:

```powershell
usbipd list
# Find the ESP busid (example: 1-5)
usbipd bind --busid <BUSID>
usbipd attach --wsl --busid <BUSID>
```

Notes:
- `bind` is persistent, so you usually do it once per device.
- `attach` is needed each time the device is re-plugged or after reboot.

Then verify again in WSL:

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Pull the docker image compatible with the microros component and link the docker files to the wsl files. 
```bash
sudo docker pull espressif/idf:release-v5.2

sudo docker run --rm -it --privileged -v "$HOME/semesterProject_LMTS/esp:/work" -w /work espressif/idf:release-v5.2
```

This container is started with `--rm`, so it is removed automatically when you exit.
If you want to keep it, run it once without `--rm` and with a name:

```bash
sudo docker run -it --privileged --name esp_idf -v "$HOME/semesterProject_LMTS/esp:/work" -w /work espressif/idf:release-v5.2
```

Then restart it later with:

```bash
sudo docker start -ai esp_idf
```

then inside the docker

Install the missing Python tooling required by the micro-ROS build (recommended before first build):

```bash
python3 -m pip install --no-cache-dir colcon-common-extensions vcstool catkin_pkg "empy==3.3.4" "lark-parser==0.12.0"
```

If you had previous failed attempts, clean intermediate folders before rebuilding:

```bash
rm -rf gripper_ctrl/build
rm -rf /work/micro_ros_espidf_component/micro_ros_src
rm -rf /work/micro_ros_espidf_component/micro_ros_dev
```

Then configure and build. In `menuconfig` set the Wi-Fi parameters. If only one USB is connected, no need to define the USB port:

```bash
cd gripper_ctrl
idf.py set-target esp32c6
idf.py menuconfig
idf.py build
idf.py flash
idf.py monitor
```

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
