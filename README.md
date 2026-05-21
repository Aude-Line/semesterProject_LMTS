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

TODO: Add build steps for `fp_bridge`.
TODO: Add run steps for `fp_bridge`

## ESP

TODO: Add build steps for `esp`.
TODO: Add run steps for `esp`.

## Run Code

TODO: Add execution steps for bridge and ESP.
