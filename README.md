# SLAM Robot Redo

A from-scratch redo of my SLAM implementation, done properly and documented
as I go, since my original attempt wasn't correctly implemented. Learning
ROS2 hands-on — building one piece at a time rather than front-loading a
full course first.

## Structure

- `notebooks/` — dev log notebooks, one per work session, documenting what
  was built, why, and the code/results at each stage
- (more folders added as the project grows — e.g. `ros2_ws/` for the actual
  ROS2 workspace once it's ready to be versioned)

## Progress

| Stage | Status |
|---|---|
| Wireless ultrasonic sensor → ROS2 pipeline | ✅ Done |
| Additional sensors | 🔜 Next |
| Gazebo simulation staging | ⏳ Planned |
| Full SLAM implementation | ⏳ Planned |

See `notebooks/` for detailed logs of each stage.

## Hardware

- Freenove 4WD Mecanum Wheel Car Kit
- Raspberry Pi Pico 2 W
- Ultrasonic sensor (more sensors TBD)

## Stack

- ROS2
- Arduino (C++) for the Pico 2 W
- Python for ROS2 nodes
