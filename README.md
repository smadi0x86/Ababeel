# Project Ababeel UAS

***Autonomous Target Classification and Deterministic Terminal Handoff for Electronic Support and Warfare in GNSS-Denied Environments***

Ababeel is an unmanned aerial system consisting of a central “mother” drone and multiple “child” drones designed to operate cooperatively. The system provides resilient communication under interference, intelligent target detection capable of distinguishing friendly (Jordanian) from unknown objects, and coordinated tracking through target lock-on and deployment mechanisms. It also includes stealth-oriented altitude management to ensure safe and efficient operation in controlled environments.

The development of Ababeel addresses the growing need for autonomous systems that can maintain reliability in disrupted communication environments and perform accurate identification of targets to prevent friendly interference. 

## Operational Scenario

Consider a hostile military vehicle, such as a tank, positioned on elevated terrain. A mother drone sets off on a mission to neutralize the target using explosive child drones carried along with it. In a heavily jammed environment where navigation systems and receiver signals are degraded or corrupted, the drone continues its mission autonomously. It achieves this by relying on alternative navigation methods, such as SLAM/VIO and satellite imagery comparison, ensuring mission success despite electronic warfare (EW) countermeasures.

## System Architecture

The project is divided into distinct subsystems, each handling a critical aspect of the mission. 

- **`es-ew/`**: Electronic Support & Electronic Warfare. Handles radar signal interception, Density Peak Clustering (DPC), Particle Filtering for tracking, and secure data link communication to munitions.
- **`vio/`**: Visual-Inertial Odometry. Provides navigation in interrupted environments by fusing stereo camera imagery and IMU data to create real-time maps and estimate drone position.
- **`targeting/`**: Target Detection. AI-based computer vision system running on edge hardware to differentiate friendly assets from hostile targets based on visual signatures and liveries.
- **`cryptography/`**: Data Security. Ensures data-at-rest protection and link hijacking prevention. Cryptographic keys reside strictly in volatile RAM, wiping sensitive data instantly upon power loss.

### Mother Drone: Autonomous Intelligence Platform
- **LiDAR Sensor (Ouster OS1-32/64)**: High-resolution 3D mapping and robust SLAM localization.
- **Inertial Unit (VectorNav VN-100)**: Low-noise, high-frequency IMU data for VINS/SLAM fusion.
- **Companion Computer (NVIDIA Jetson Orin Nano / Intel NUC)**: Dedicated processing power for real-time AI, VINS, and SLAM computation.
- **Stereo Camera (ZED Mini or RealSense D435i)**: Visual and depth data for VIO, enhancing spatial awareness.
- **Flight Controller (Holybro Pixhawk 6C/CubePilot)**: Executes precise SO(3) control signals for stable flight.

### Child Drone: Secondary Unit
- **Flight Controller (FPV AIO Stack F4/F7)**: Lightweight, minimal flight controller for basic stability and maneuver execution.
- **Terminal Sensor (FPV Camera + Basic Nav)**: Visual seeker for tracking and lock-on, providing baseline positional data.

## Development Phases

1. **Project Study and Conceptual Design**: Defined the problem statement, reviewed related work, selected hardware, and validated theoretical communication models and VIO/SLAM concepts.
2. **Simulation and Validation**: Implemented core logic in simulated environments (e.g., Gazebo). Tested image classification systems and verified logic flows and acceptable system latencies.
3. **Prototyping and System Integration**: Hardware wiring, embedded firmware development, deployment of optimized AI models onto edge computers, and functional linking of mother and child drones. Concluded with field tests.

## Reflections

- **ES/EW**: Transitioned from Extended Kalman Filters to Particle Filters to handle erratic drone dynamics. Shifted to Density-Based Clustering to isolate unknown radar signals autonomously. Implemented bit-level packing for the data link to remove transmission delays.
- **VIO**: Proved effective as a backup for navigation interrupted environments. Identified that map accuracy heavily depends on environmental details; added features like rotational take-off scanning significantly improved initial spatial awareness.
- **Targeting**: Achieved ~95% success rate in distinguishing friendly from hostile targets using visual liveries, optimized for the NVIDIA Jetson architecture.
- **Cryptography**: Shifted from post-flight file encryption to real-time, pre-storage encryption. Designed a volatile RAM key lifecycle to ensure captured drones yield no unencrypted data.

## Strategic Vision

Our ultimate aim extends beyond connecting one drone to one munition. We intend to develop our data link into a proprietary communication standard, i.e., a standardized Interface Control Document (ICD) for our drone ecosystem. This transforms Ababeel from a single prototype into a scalable, interoperable defense architecture for unmanned aerial systems with strict size, weight, and power constraints.