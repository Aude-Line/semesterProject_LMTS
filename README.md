# semesterProject_LMTS

## Intro

This repository contains the work carried out during a semester project in which a silicone gripper powered by an EHD pump was developed and mounted on a P-Rob3 robot. The robot and gripper were then integrated into ROS 2 to perform a pick-and-place task.

## Structure of This Repo

Main folders:

- `fp_bridge`: bridge code to connect to the robot ROS node (Git submodule)
- `esp`: ESP code (Git submodule)
- `hardware`: contains electronics, CAD file and mechanical setup

## Version compatibility

This project is developed in WSL2 on Ubuntu 22.04.

### Robot context:

The robot runs a `roscore` instance that provides the basic robot commands. Since this interface is based on ROS 1 rather than ROS 2, an additional compatibility layer had to be introduced using `ros1_bridge`.
The `fp` library version compatible with the robot software (`myP` 1.4.4) was modified to generate readable ROS 1 messages and services. A ROS 2 side was then implemented with custom mapping rules.

### ROS / bridge context:

- ROS 2 side: Humble built from sources on Ubuntu 22.04
- ROS 1 side: `ros-core-dev` on Ubuntu 22.04 (Jammy upstream setup for `ros1_bridge`)
- Bridge context: humble with upstream to be able to use bool patch -> less stable

The bridge code was also modified to be able to use personal class tables (Joints[])

with custom mapping rules the bridge needs to be recompiled, but as I modified it it needed to be recompiled anyway

Reference guides:
https://docs.ros.org/en/humble/How-To-Guides/Using-ros1_bridge-Jammy-upstream.html

https://docs.ros.org/en/humble/p/ros1_bridge/doc/index.html

### ESP context:

The ESP-C6 dev board was selected because it was expected to be compatible with the micro-ROS component for ROS 2 Humble. During testing, we found that it was not fully compatible out of the box: the ESP-C6 does not include a floating-point unit (FPU), so the micro-ROS component had to be adapted accordingly.

To avoid adding extra setup steps, prebuilt Docker images were used to run the micro-ROS agent and access ESP-IDF tooling.

Reference guide:
https://github.com/micro-ROS/micro_ros_espidf_component/tree/humble

## WSL Setup

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

## Clone project

Clone the project with all submodules (including submodules inside submodules) inside wsl:

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

## Build and Setup Details

Detailed build and setup instructions are provided in the sub-READMEs:

- ROS 1 / ROS 2 installation and bridge build steps: see `fp_bridge/README.md`
- ESP build and flashing steps: see `esp/README.md`
- Electronics and mechanical setup: see `hardware/README.md`

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

The agent must run in its own terminal to establish the connection between the ESP and the computer.

Then we assume that the code is already flashed on the esp (see `esp/README.md`) and chose the same connection method.

#### USB connection

If you are using a USB connection, first identify the correct USB port.

Check which port is available. If no port is visible, re-attach the device from PowerShell as Administrator (see `esp/README.md`).
```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Then start the agent on the detected port (USB0 is a standard for wsl):
```bash
sudo docker run -it --rm --net=host --device=/dev/ttyUSB0 microros/micro-ros-agent:humble serial --dev /dev/ttyUSB0 -b 115200 -v6
```

#### Wi-Fi connection

If you are using a wireless connection, start the agent with UDP:
```bash
sudo docker run -it --rm --net=host microros/micro-ros-agent:humble udp4 --port 8888 -v6
```

With a wireless connection, you can open another terminal to monitor the ESP (see `esp/README.md`). With a USB connection, this is not possible because the UART is already being used by the agent. Make sure that both the esp and the host are on the same wifi.

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
