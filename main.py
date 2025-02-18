# Required imports
import cv2 
import numpy as np  
import math 
import random  
from dataclasses import dataclass # Dataclass for storing game settings
from typing import Tuple, List
from cvzone.HandTrackingModule import HandDetector  #
import cvzone  #

# Configuration class to store all game settings
@dataclass
class GameConfig:
    WINDOW_WIDTH: int = 1280  
    WINDOW_HEIGHT: int = 720  
    INITIAL_SNAKE_LENGTH: int = 150  
    LENGTH_INCREMENT: int = 50 
    DETECTION_CONFIDENCE: float = 0.8  
    FOOD_PATH: str = "Donut.png"  
    CIRCLE_RADIUS: int = 20  
    LINE_THICKNESS: int = 20  

class SnakeGame:

    def __init__(self, config: GameConfig):
        self.config = config
        self.points: List[Tuple[int, int]] = []  # List of points forming the snake's body
        self.lengths: List[float] = []  # List of distances between consecutive points
        self.current_length: float = 0  # Current length of the snake
        self.allowed_length: int = config.INITIAL_SNAKE_LENGTH  # Maximum allowed length
        self.previous_head: Tuple[int, int] = (0, 0)  # Previous position of snake's head
        self.score: int = 0  # Current game score
        self.game_over: bool = False  # Game over flag
        
        # Load and initialize food image
        self.food_img = cv2.imread(config.FOOD_PATH, cv2.IMREAD_UNCHANGED)
        if self.food_img is None:
            raise FileNotFoundError(f"Food image not found: {config.FOOD_PATH}")
        self.food_height, self.food_width = self.food_img.shape[:2]  # Get food image dimensions
        self.food_location = self._generate_food_location()  # Initial food position

    def _generate_food_location(self) -> Tuple[int, int]:
        padding = 100  # Padding from window edges
        x = random.randint(padding, self.config.WINDOW_WIDTH - padding)
        y = random.randint(padding, self.config.WINDOW_HEIGHT - padding)
        return x, y

    def _check_food_collision(self, head_pos: Tuple[int, int]) -> bool:
    
        x, y = head_pos
        food_x, food_y = self.food_location
        return (abs(x - food_x) < self.food_width // 2 and 
                abs(y - food_y) < self.food_height // 2)

    def _check_self_collision(self, head_pos: Tuple[int, int]) -> bool:
        
        if len(self.points) < 3:  # Not enough points for self-collision
            return False
        
        # Convert points to numpy array for collision detection
        points = np.array(self.points[:-2], np.int32).reshape((-1, 1, 2))
        distance = cv2.pointPolygonTest(points, head_pos, True)
        return -1 <= distance <= 1  # Collision threshold

    def _update_snake_length(self, new_point: Tuple[int, int]):
       
        # Calculate distance between new point and previous head
        dx = new_point[0] - self.previous_head[0]
        dy = new_point[1] - self.previous_head[1]
        distance = math.hypot(dx, dy)
        
        # Add new point and its distance
        self.points.append(new_point)
        self.lengths.append(distance)
        self.current_length += distance
        
        # Remove excess length from the tail
        while self.current_length > self.allowed_length and self.lengths:
            self.current_length -= self.lengths.pop(0)
            self.points.pop(0)

    def reset(self):
       
        self.points.clear()
        self.lengths.clear()
        self.current_length = 0
        self.allowed_length = self.config.INITIAL_SNAKE_LENGTH
        self.previous_head = (0, 0)
        self.score = 0
        self.game_over = False
        self.food_location = self._generate_food_location()

    def update(self, frame: np.ndarray, head_pos: Tuple[int, int]) -> np.ndarray:
        
        if self.game_over:
            self._draw_game_over(frame)
            return frame
            
        self._update_snake_length(head_pos)
        
        # Check collisions and update game state
        if self._check_food_collision(head_pos):
            self.allowed_length += self.config.LENGTH_INCREMENT
            self.score += 1
            self.food_location = self._generate_food_location()
        elif self._check_self_collision(head_pos):
            self.game_over = True
            return frame

        # Draw game elements
        self._draw_snake(frame)
        
        # Draw food at current location
        food_x, food_y = self.food_location
        frame = cvzone.overlayPNG(frame, self.food_img,
                                (food_x - self.food_width // 2,
                                 food_y - self.food_height // 2))
        
        # Draw score
        cvzone.putTextRect(frame, f'Score: {self.score}', [50, 80],
                          scale=3, thickness=3, offset=10)
        
        self.previous_head = head_pos
        return frame

    def _draw_snake(self, frame: np.ndarray):
       
        if not self.points:
            return
            
        # Draw snake body segments
        for i in range(1, len(self.points)):
            cv2.line(frame, self.points[i - 1], self.points[i],
                    (0, 0, 255), self.config.LINE_THICKNESS)
            
        # Draw snake head
        cv2.circle(frame, self.points[-1], self.config.CIRCLE_RADIUS,
                  (200, 0, 200), cv2.FILLED)

    def _draw_game_over(self, frame: np.ndarray):
       
        cvzone.putTextRect(frame, "Game Over", [250, 350],
                          scale=8, thickness=4,
                          colorT=(255, 255, 255),
                          colorR=(0, 0, 255), offset=20)
        cvzone.putTextRect(frame, f'Final Score: {self.score}',
                          [250, 500], scale=8, thickness=5,
                          colorT=(255, 255, 255),
                          colorR=(0, 0, 255), offset=20)

def main():
   
    # Initialize game configuration
    config = GameConfig()
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    cap.set(3, config.WINDOW_WIDTH)
    cap.set(4, config.WINDOW_HEIGHT)
    
    # Initialize hand detector with configuration settings
    detector = HandDetector(detectionCon=config.DETECTION_CONFIDENCE,
                          maxHands=1)
    
    # Create game instance
    game = SnakeGame(config)
    
    # Main game loop
    while True:
        # Read frame from camera
        success, frame = cap.read()
        if not success:
            print("Failed to read frame")
            break
            
        # Flip frame horizontally for natural movement
        frame = cv2.flip(frame, 1)
        # Detect hands in the frame
        hands, frame = detector.findHands(frame, flipType=False)
        
        if hands:
            # Get position of index finger tip
            index_finger_tip = hands[0]['lmList'][8][:2]
            frame = game.update(frame, index_finger_tip)
        
        # Display the game
        cv2.imshow("Snake Game", frame)
        
        # Handle keyboard input
        key = cv2.waitKey(1)
        if key == ord('r'):  # Reset game
            game.reset()
        elif key == ord('q'):  # Quit game
            break
    
    # Clean up resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()