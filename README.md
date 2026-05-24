# semesterProject_LMTS

## Intro

TODO: Add a short project overview.

## Structure of This Repo

Main folders:

- `fp_bridge`: bridge code to connect to the robot ROS node (Git submodule)
- `esp`: ESP code (Git submodule)
- `hardware`: contains electronics, CAD file and mechanical setup

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

## WSL Setup

This project is developed in WSL2 on Ubuntu 22.04.

ROS / bridge context:

- ROS 2 side: Humble built from sources on Ubuntu 22.04
- ROS 1 side: `ros-core-dev` on Ubuntu 22.04 (Jammy upstream setup for `ros1_bridge`)
- Bridge context: humble with upstream to be able to use bool patch -> less stable

The bridge code was also modified to be able to use personal class tables (Joints[])

The fp library was modified to generate readable ROS1 msg and srv, and a ROS2 side was implemented, with custom mapping rules

with custom mapping rules the bridge needs to be recompiled, but as I modified it it needed to be recompiled anyway

Reference guides:
https://docs.ros.org/en/humble/How-To-Guides/Using-ros1_bridge-Jammy-upstream.html

https://docs.ros.org/en/humble/p/ros1_bridge/doc/index.html

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

## Build Setup Details

Build and setup details are kept in the sub-READMEs:

- `fp_bridge`: see `fp_bridge/README.md`
- `esp`: see `esp/README.md`

## Run Code

This section assumes that all builds are already done, all the connections are working, and the file is already uploaded on the ESP.

Open the terminals in this order.

remainder in case you forgot your IP use
```bash
hostname -I
```

### Terminal 1 - ROS1 bridge
The bridge needs to run (in its own terminal) to allows the connection between the computer and the ROS1 node on the robot
```bash
source ~/semesterProject_LMTS/fp_bridge/ros1_ws/devel/setup.bash
source ~/ros2_humble/install/setup.bash
source ~/semesterProject_LMTS/fp_bridge/ros2_ws/install/setup.bash
source ~/semesterProject_LMTS/fp_bridge/bridge_ws/install/setup.bash

export ROS_MASTER_URI=http://10.0.0.203:11311
export ROS_IP=<yourIP>

ros2 run ros1_bridge dynamic_bridge --bridge-all-topics
```

### Terminal 2 - micro-ROS agent

The agent must run in its own terminal to establish the connection between the ESP and the computer. Start the agent first, then power or reboot the ESP so the code on the ESP starts only after the agent is active.

if using usb connection:
```bash
sudo docker run -it --rm --net=host microros/micro-ros-agent:humble udp4 --port 8888 -v6
```

if using wireless connection:
```bash
sudo docker run -it --rm --net=host microros/micro-ros-agent:humble udp4 --port 8888 -v6
```

With a wireless connection, you can open another terminal to monitor the ESP (see `esp/README.md`). With a USB connection, this is not possible because the UART is already used by the agent communication.

### Terminal 3 - gripper interface

This script publishes gripper commands to the ESP topic and also calls robot services
(`connect`, `disconnect`, `home`, `gotarget`, `goplace`, etc.).

Start a new terminal then run the next cell to source ROS2 and the robot workspace and start the python script

```bash
source /home/fleur/ros2_humble/install/local_setup.bash
source /home/fleur/semesterProject_LMTS/fp_bridge/ros2_ws/install/local_setup.bash

export ROS_MASTER_URI=http://10.0.0.203:11311
export ROS_IP=<yourIP>

cd ~/semesterProject_LMTS
python3 gripper_interface.py
```

Typical command flow inside the interface:

```text
connect
home
target x y z angle
gotarget
open
close
disconnect
q
```
