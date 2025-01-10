import cvzone
import cv2
import numpy as np
import math
import random
from cvzone.HandTrackingModule import HandDetector

# setup openCV capture and window size
capture = cv2.VideoCapture(0)
capture.set(3, 1280)
capture.set(4, 720)

detect = HandDetector(detectionCon=0.8, maxHands=1)


class snakeCVclass:
    def __init__(self, foodPath):
        self.point = []  # Points of the snake
        self.length = []  # Distance between points
        self.currentLength = 0  # Total snake length
        self.TotalAllowedLength = 150  # Total allowed length
        self.headPrevious = 0, 0  # Previous head point.

        # Food initialization
        self.foodIMG = cv2.imread(foodPath, cv2.IMREAD_UNCHANGED)  # import the food image
        self.foodHeight, self.foodWidth, _ = self.foodIMG.shape  # setting the food height and width based on the foodimg shape
        self.foodLocation = 0, 0  # food location (or points)
        self.FoodLocationRandom()  # initialize the random function
        self.score = 0  # Game Score
        self.gameOver = False  # see if the game is over

    # set the food location
    def FoodLocationRandom(self):
        self.foodLocation = random.randint(100, 1000), random.randint(100, 600)

    def update(self, mainIMG, headCurrent):

        if self.gameOver:
            cvzone.putTextRect(mainIMG, "Game Over", [250, 350], scale=8, thickness=4, colorT=(255, 255, 255),
                               colorR=(0, 0, 255), offset=20)
            cvzone.putTextRect(mainIMG, f'Your Score: {self.score}', [250, 500], scale=8, thickness=5,
                               colorT=(255, 255, 255), colorR=(0, 0, 255), offset=20)
        else:
            # Break down the previous and current points location to x and y
            previousX, previousY = self.headPrevious
            currentX, currentY = headCurrent

            # Find the distance between the previous and the current point.
            self.point.append([currentX, currentY])
            distance = math.hypot(currentX - previousX,
                                  currentY - previousY)  # distance = sqrt([currentX - previousX]^2 + [currentY - previousY]^2)
            self.length.append(distance)
            self.currentLength += distance
            self.headPrevious = currentX, currentY

            # Reducing Length if current length exceeds the allowed length
            if self.currentLength > self.TotalAllowedLength:
                for i, length in enumerate(self.length):
                    self.currentLength -= length
                    self.length.pop(i)  # Remove the subtracted length in index i
                    self.point.pop(i)  # Remove the point corresponding to the removed length

                    # Check if the current length has become less than the total allowed length
                    if self.currentLength < self.TotalAllowedLength:
                        break

            # check if snake ate the food
            randomX, randomY = self.foodLocation
            if (
                    randomX - self.foodWidth // 2 < currentX < randomX + self.foodWidth // 2  # Check if the currentX and currentY coordinates of the snake has touched the boundaries of the food
                    and randomY - self.foodHeight // 2 < currentY < randomY + self.foodHeight // 2):
                self.FoodLocationRandom()
                self.TotalAllowedLength += 50
                self.score += 1
                print(self.score)

            # Draw the line
            if self.point:
                for i, point in enumerate(self.point):
                    if i != 0:
                        cv2.line(mainIMG, self.point[i - 1], self.point[i], (0, 0, 255),
                                 20)  # cv2.line(image, start_point, end_point, color, thickness)
                cv2.circle(img, self.point[-1], 20, (200, 0, 200), cv2.FILLED)

            # collision check
            point = np.array(self.point[:-2], np.int32)
            point = point.reshape((-1, 1, 2))
            cv2.polylines(mainIMG, [point], False, (0, 200, 0), 3)
            minDist = cv2.pointPolygonTest(point, (currentX, currentY), True)

            # check if the collision happens
            if -1 <= minDist <= 1:
                print("hit")
                self.gameOver = True
                self.point = []
                self.length = []
                self.currentLength = 0
                self.TotalAllowedLength = 150
                self.headPrevious = 0, 0
                self.FoodLocationRandom()

                # Draw food
            randomX, randomY = self.foodLocation
            mainIMG = cvzone.overlayPNG(mainIMG, self.foodIMG,
                                        (randomX - self.foodWidth // 2, randomY - self.foodHeight // 2))

            # showScore
            cvzone.putTextRect(mainIMG, f'Your Score :{self.score}', [50, 80], scale=3, thickness=3, offset=10)

        return mainIMG


game = snakeCVclass("Donut.png")
restart_game = False

while True:
    success, img = capture.read()  # Read a frame from the video capture
    img = cv2.flip(img, 1)  # Flip the camera horizontally
    hand, img = detect.findHands(img, flipType=False)  # Detect hands in the camera

    if hand:
        landmarkList = hand[0]['lmList']  # Get the landmark list for the detected hand
        pointIndex = landmarkList[8][0:2]  # Get the location of the index finger tip
        img = game.update(img, pointIndex)

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('r'):
        game.gameOver = False
        game.score = 0  # Reset the score to 0
        restart_game = True

    if restart_game:
        game = snakeCVclass("Donut.png")  # Create a new instance of the game object
        restart_game = False

    if key == ord('q'):
        break