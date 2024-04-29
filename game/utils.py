import mediapipe as mp
import math
import cv2
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt
import tty, termios, sys


mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

def distance(a, b):
    return math.sqrt(math.pow((b[0]-a[0]),2)+math.pow(b[1]-a[1],2))

def getCordLists(frame, result):
    current_x_cord = list()
    current_y_cord = list()

    for _, lm in enumerate(result.pose_landmarks.landmark):
        h, w, _ = frame.shape
        current_x_cord.append(int(lm.x * w))
        current_y_cord.append(int(lm.y * h))
        
    return current_x_cord, current_y_cord

def bounding_box_cordinates(x_cord_list, y_cord_list):
    top_y = min(y_cord_list)
    bottom_y = max(y_cord_list)
    left_x = min(x_cord_list)
    right_x = max(x_cord_list)
    for i in range(len(x_cord_list)):
        if x_cord_list[i] == left_x:
            left_pt = (x_cord_list[i], y_cord_list[i])
        elif x_cord_list[i] == right_x:
            right_pt = (x_cord_list[i], y_cord_list[i])
    for i in range(len(y_cord_list)):
        if y_cord_list[i] == top_y:
            top_pt = (x_cord_list[i], y_cord_list[i])
        elif y_cord_list[i] == bottom_y:
            bottom_pt = (x_cord_list[i], y_cord_list[i])

    corner_high = int(distance(a=left_pt, b=top_pt) / math.sqrt(2))
    corner_low = int(distance(a=bottom_pt, b=right_pt) / math.sqrt(2))

    top_left_corner = (top_pt[0] - corner_high-20, top_pt[1]-85)
    bottom_right_corner = (bottom_pt[0] + corner_low-50, bottom_pt[1])

    return top_left_corner, bottom_right_corner


def frame2QtImage(frame, width, height):
    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, ch = rgbImage.shape
    bytesPerLine = ch * w
    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
    p = convertToQtFormat.scaled(width, height, Qt.KeepAspectRatio)
    return p

def getchar():
   fd = sys.stdin.fileno()
   old_settings = termios.tcgetattr(fd)
   try:
      tty.setraw(sys.stdin.fileno())
      ch = sys.stdin.read(1)
   finally:
      termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
   return ch