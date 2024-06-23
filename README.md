# Finger Control Ping-Pong Game

## Introduction

This project is a ping-pong game controlled by finger movements detected using OpenCV. The game tracks the player's finger movements and translates these real-world coordinates to control the paddle in the game.

## Requirements

- Python 3.x
- OpenCV
- Numpy
- Pygame

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/finger-control-ping-pong.git
   cd finger-control-ping-pong
   ```
 
2. **Install the dependencies:**
    ```bash
    pip install opencv-python numpy pygame
    ```

## How It Works
The project uses OpenCV to capture video from the webcam and detect finger movements. The detected coordinates are then mapped to the game's coordinate system to control the paddle.

## Future Improvements
- Enhance finger detection accuracy
- Add more game features like scoring and levels
- Implement a better mapping between real-world coordinates and game controls

## License
This project is licensed under the [MIT License](https://github.com/Drownie/Finger-Control-Ping-Pong/blob/master/LICENSE). See the LICENSE file for details.
