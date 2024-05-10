from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5 import QtCore
import sys
import cv2
import time
import threading
import mediapipe as mp
from pygame import mixer
from enum import Enum
from utils import bounding_box_cordinates, frame2QtImage, getCordLists

mixer.init()

def theme_sound():
    mixer.music.load('sounds/theme2.wav')
    mixer.music.play(-1)

def win_sound():
    mixer.music.load('sounds/win.wav')
    mixer.music.play()

def click_sound():
    mixer.music.load('sounds/click.wav')
    mixer.music.play()


def red_light_sound():
    mixer.music.load('sounds/red-light.wav')
    mixer.music.play()


def gun_shoot_sound():
    mixer.music.load('sounds/gun-shoot.wav')
    mixer.music.play()


def turning_sound():
    time.sleep(1)
    mixer.music.load('sounds/turning.wav')
    mixer.music.play()


def scanning_sound():
    mixer.music.load('sounds/scanning.wav')
    mixer.music.play()


def movement_detected_sound():
    mixer.music.load('sounds/beep.wav')
    mixer.music.play()


class GameState(Enum):
    INIT = 0
    STARTED = 1
    LOSE = 2
    WIN = 3

class Thread(QThread):
    changeColorImage = pyqtSignal(QImage)
    changeBWImage = pyqtSignal(QImage)
    changeState = pyqtSignal(GameState)
    
    def __init__(self, parent=None):
        super(Thread, self).__init__(parent)
        self.cap = None
    
    def stop(self):
         if self.cap is not None:
            self.cap.release()

    def run(self):
        self.cap = cv2.VideoCapture(0)
        mpPose = mp.solutions.pose
        pose = mpPose.Pose()

        _, start_frame = self.cap.read()
        start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
        start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)
        
        alarm = False     
        alarm_counter = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            result = pose.process(frame)
            
            if result.pose_landmarks:
                current_x_cord, current_y_cord = getCordLists(frame, result)
                pt1, pt2 = bounding_box_cordinates(x_cord_list=current_x_cord, y_cord_list=current_y_cord)
                
                frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)
                difference = cv2.absdiff(frame_bw, start_frame)
                threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
                start_frame = frame_bw
                
                if threshold.sum() > 300:
                    if alarm_counter < 10:
                        alarm_counter += 1
                elif alarm_counter > 0:
                    alarm_counter -= 1
                
                if alarm_counter == 10:
                    if not alarm:
                        alarm = True
                        self.changeState.emit(GameState.LOSE)
                        cv2.rectangle(frame, pt1, pt2, (0,0,255), 3)
                        threading.Thread(target=gun_shoot_sound).start()
                        self.stop()
                else:
                    cv2.rectangle(frame, pt1, pt2, (0,255,0), 3)
                    alarm = False
                    
                self.changeColorImage.emit(frame2QtImage(frame, 1000, 900))
                self.changeBWImage.emit(frame2QtImage(threshold, 550, 550))

class App(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.title = 'Red Light, Green Light'
        self.left = 0
        self.top = 0
        self.width = 1920
        self.height = 1080

        self.gameState = GameState.INIT
        self.rounds = 0
        self.initUI()

    def keyPressEvent(self, event):
        
        key = event.key()
        if key == Qt.Key_Q:
            self.home()

    def initUI(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.label = QLabel(self)
        self.pixmap = QPixmap('images/home/background.jpeg')
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.width, self.height)
        self.label.setHidden(True)

        self.title = QLabel(self)        
        self.pixmap = QPixmap('images/home/title.png')
        self.title.setPixmap(self.pixmap)
        self.title.resize(self.pixmap.width(), self.pixmap.height())
        self.title.move(360, 90)
        self.title.setHidden(True)

        self.start_button = QPushButton("", self)
        self.start_button.setGeometry(1400,850,300,110)
        self.start_button.setStyleSheet("background-image : url(images/home/play.png); border : 0px solid black")
        self.start_button.clicked.connect(self.start_game)
        self.start_button.setHidden(True)
        
        self.test_button = QPushButton("", self)
        self.test_button.setGeometry(685,850,550,110)
        self.test_button.setStyleSheet("background-image : url(images/home/test-camera.png); border : 0px solid black")
        self.test_button.clicked.connect(self.test_camera)
        self.test_button.setHidden(True)

        self.quit_button = QPushButton("", self)
        self.quit_button.setGeometry(225,850,300,110)
        self.quit_button.setStyleSheet("background-image : url(images/home/exit.png); border : 0px solid black")
        self.quit_button.clicked.connect(self.close)
        self.quit_button.setHidden(True)

        self.red_light = QLabel(self)
        self.pixmap = QPixmap('images/red-light.jpg')
        scaled_pixmap = self.pixmap.scaledToWidth(400)
        self.red_light.setPixmap(scaled_pixmap)
        self.red_light.resize(scaled_pixmap.width(), scaled_pixmap.height())
        self.red_light.move(170, 40)
        self.red_light.setHidden(True)
        
        self.green_light = QLabel(self)        
        self.pixmap = QPixmap('images/green-light.jpg')
        self.green_light.setPixmap(self.pixmap)
        self.green_light.resize(self.pixmap.width(), self.pixmap.height())
        self.green_light.move(0,0)
        self.green_light.setHidden(True)

        self.home()
        
    def home(self):
        theme_sound()
        self.pixmap = QPixmap('images/home/background.jpeg')
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.width, self.height)
        self.label.setHidden(False)
        self.title.setHidden(False)
        self.start_button.setHidden(False)
        self.test_button.setHidden(False)
        self.quit_button.setHidden(False)
        self.show()

    def test_camera(self):
        cap = cv2.VideoCapture(0)  
        
        while True:
            _, frame = cap.read()
            cv2.imshow('frame', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break        
        
        cap.release()
        cv2.destroyAllWindows()
        
    def win_game(self):
        win_sound()
        self.label.setHidden(False)
        self.pixmap = QPixmap('images/win.png')
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.width, self.height)
        
    def lose_game(self):
        self.label.setHidden(False)
        self.pixmap = QPixmap('images/lose.png')
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.width, self.height-50)
        
    def setColorImage(self, image):
        self.color_img.setPixmap(QPixmap.fromImage(image))
        
    def setBWImage(self, image):
        self.bw_img.setPixmap(QPixmap.fromImage(image))
        
    def setState(self, state):
        self.gameState = state
    
    def start_game(self):

        click_sound()
        self.gameState = GameState.STARTED
        self.setStyleSheet("background-color: lightblue;")

        self.start_button.setHidden(True)
        self.test_button.setHidden(True)
        self.quit_button.setHidden(True)
        self.label.setHidden(True)
        self.title.setHidden(True)
        self.green_light.setHidden(False)

        loop = QtCore.QEventLoop()

        red_light_sound()
        QtCore.QTimer.singleShot(5000, loop.quit)
        loop.exec_()

        turning_sound()
        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec_()

        self.green_light.setHidden(True)
        self.red_light.setHidden(False)

        self.color_img = QLabel(self)
        self.color_img.move(850,40)
        self.color_img.resize(1000,900)
        self.color_img.setHidden(False)
        
        self.bw_img = QLabel(self)
        self.bw_img.resize(550, 550)
        self.bw_img.move(100, 450)
        self.bw_img.setHidden(False)

        #--------------------------------------------
        th = Thread(self)
        th.changeColorImage.connect(self.setColorImage)
        th.changeState.connect(self.setState)
        th.changeBWImage.connect(self.setBWImage)
        th.start()

        scanning_sound()
        QtCore.QTimer.singleShot(7000, loop.quit)
        loop.exec_()

        th.stop()
        #--------------------------------------------

        self.red_light.setHidden(True)
        self.color_img.setHidden(True)
        self.bw_img.setHidden(True)

        if self.gameState == GameState.LOSE:
            self.lose_game()
            return
        
        self.rounds += 1
        if(self.rounds == 1):
            self.win_game()
            return
        else:
            self.start_game()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())