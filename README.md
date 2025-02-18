# Snake Game using OpenCV and Hand Tracking

## Overview
This project implements a Snake Game using OpenCV for video capture and hand tracking, leveraging the `cvzone` library. The game is controlled by the user's hand movements detected through a webcam.

## Features
- Real-time hand tracking to control the snake.
- Uses OpenCV for video processing.
- Randomly generated food locations.
- Collision detection for food and self-collision.
- Game over screen when the snake collides with itself.

## Installation
### Prerequisites
Ensure you have Python installed on your system. Then, install the required dependencies using:

```bash
pip install opencv-python cvzone numpy mediapipe
```

## How to Run
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/snake-game-opencv.git
   ```
2. Navigate to the project directory:
   ```bash
   cd snake-game-opencv
   ```
3. Run the game script:
   ```bash
   python main.py
   ```

## Classes and Functions
### `GameConfig`
A configuration class storing all game settings.
#### Attributes:
- `WINDOW_WIDTH (int)`: Width of the game window.
- `WINDOW_HEIGHT (int)`: Height of the game window.
- `INITIAL_SNAKE_LENGTH (int)`: Initial length of the snake.
- `LENGTH_INCREMENT (int)`: Length increment when the snake eats food.
- `DETECTION_CONFIDENCE (float)`: Confidence threshold for hand detection.
- `FOOD_PATH (str)`: Path to the food image.
- `CIRCLE_RADIUS (int)`: Radius of the snake's head circle.
- `LINE_THICKNESS (int)`: Thickness of the snake's body lines.

### `SnakeGame`
The main class handling game logic and rendering.
#### Methods:
- `__init__(config: GameConfig)`: Initializes the game with the given configuration.
- `_generate_food_location() -> Tuple[int, int]`: Generates a random location for the food.
- `_check_food_collision(head_pos: Tuple[int, int]) -> bool`: Checks if the snake's head collides with the food.
- `_check_self_collision(head_pos: Tuple[int, int]) -> bool`: Checks if the snake's head collides with its body.
- `_update_snake_length(new_point: Tuple[int, int])`: Updates the snake's length and removes excess length from the tail.
- `reset()`: Resets the game state.
- `update(frame: np.ndarray, head_pos: Tuple[int, int]) -> np.ndarray`: Updates the game state and renders the frame.
- `_draw_snake(frame: np.ndarray)`: Draws the snake on the frame.
- `_draw_game_over(frame: np.ndarray)`: Draws the game over screen on the frame.

### `main()`
- Initializes the game configuration, video capture, and hand detector.
- Runs the main game loop.

## Controls
- Move your hand in front of the webcam to control the snake’s movement.
- The snake follows your hand’s position.
- The game ends when the snake collides with itself.

## Future Improvements
- Adding different difficulty levels.
- Implementing sound effects.
- High-score tracking.
- Multi-hand support for multiplayer mode.

## License
This project is licensed under the MIT License. Feel free to modify and distribute it as needed.
