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

With custom mapping rules, the bridge needs to be recompiled; since it was already modified, it had to be recompiled anyway.

Reference guides:
https://docs.ros.org/en/humble/How-To-Guides/Using-ros1_bridge-Jammy-upstream.html

https://docs.ros.org/en/humble/p/ros1_bridge/doc/index.html

### ESP context:

The ESP-C6 dev board was selected because it was expected to be compatible with the micro-ROS component for ROS 2 Humble. During testing, we found that it was not fully compatible out of the box: the ESP-C6 does not include a floating-point unit (FPU), so the micro-ROS component had to be adapted accordingly.

To avoid adding extra setup steps, prebuilt Docker images were used to run the micro-ROS agent and access ESP-IDF tooling.

Reference guide:
https://github.com/micro-ROS/micro_ros_espidf_component/tree/humble

## WSL Setup

Reference guide: 
https://learn.microsoft.com/en-us/windows/wsl/install
https://learn.microsoft.com/en-us/windows/wsl/networking#mirrored-mode-networking

### 0) Install WSL

### 1) Enable mirror mode networking (optional but recommended)

Mirror mode makes WSL share the same network interfaces as Windows (same IP, LAN access, VPN compatibility). This fixed connection issues between WSL and the "outside" connections during the first tests (Robot, ESP).

Create or edit the file `%USERPROFILE%\.wslconfig` on Windows:
```powershell
notepad "$env:USERPROFILE\.wslconfig"
```

```ini
[wsl2]
networkingMode=mirrored
```

Then restart WSL from PowerShell:

```powershell
wsl --shutdown
```

### 2) Install a dedicated distro for this project (PowerShell)
This will create a new Ubuntu 22.04 instance named Ubuntu-22.04-fpRob; the name can be changed as you wish.

```powershell
wsl --install Ubuntu-22.04 --name Ubuntu-22.04-fpRob --version 2 --web-download
```

During first launch, create your Linux user and set a password.

### 3) Launch the project distro (PowerShell)
use the name set at the last step

```powershell
wsl -d Ubuntu-22.04-fpRob
```

### 4) Verify WSL version (PowerShell)

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

Open the terminals in this order. If nothing is specified, consider that the terminal is a WSL instance. Don't forget to start the right WSL instance.

Reminder: the IP address of your Linux distribution installed via WSL 2 is obtained in a wsl environment via
```bash
hostname -I
```

or in a windows terminal
```bash
wsl hostname -I
```

Two network constraints drive the required setup:
- The robot only accepts connections from a computer on the EPFL Wi-Fi.
- The ESP cannot connect to the EPFL Wi-Fi (incompatible authentication protocol), but works fine on other networks (home Wi-Fi, 5G hotspot).

Since both constraints cannot be satisfied over Wi-Fi simultaneously, **the ESP must communicate with the computer via USB**, and **the robot must communicate with the computer via Ethernet**, while the computer remains connected to the EPFL Wi-Fi.

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

This assumes that the code is already flashed on the ESP (see `esp/README.md`) using the same connection method.

#### USB connection

First identify the correct USB port.

Check which port is available. 
```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

If no port is visible, re-attach the device from PowerShell as Administrator (see `esp/README.md` for full pipe line). This needs to be done every time the usb is disconnected.
```powershell
usbipd list
```
```powershell
usbipd attach --wsl --busid <BUSID>
```


Then start the agent on the detected port (USB0 is a standard for wsl):
```bash
sudo docker run -it --rm --net=host --device=/dev/ttyUSB0 microros/micro-ros-agent:humble serial --dev /dev/ttyUSB0 -b 115200 -v6
```

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
place x y z angle
gotarget
goplace
open
close
disconnect
q
```

Both `target` and `place` use the same parameters:
x, y, z position in mm in the robot frame. The angle is the orientation of the tool in degrees. It takes only one angle as a parameter, as the other two axes are forced to be parallel to the table.

`gotarget` is a movement command. It first moves up slightly from the current position, then moves above the set target, then moves down to reach it. `goplace` works on the same principle, but for the place point.
Note: this version does not account for joint limits and blindly trusts the robot's embedded controller. For some positions, normally generated trajectories may reach the joint limits; the embedded controller still performs the move, but by first putting the robot in an upward position. Test the trajectories and use small ones for safety.

Example that worked well:
target -320 -210 160 -70
place -10 -400 200 -90

Don't forget to call `home` to put the robot in the upward position before calling `disconnect`, so the robot doesn't fall.