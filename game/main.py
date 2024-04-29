from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5 import QtCore
import sys
import cv2
import mediapipe as mp
from calculations import extract_cordinates, check_movement_range, bounding_box_cordinates
import csv
from pygame import mixer
import time

mixer.init()


def theme_sound():
    mixer.music.load('sounds/theme2.wav')
    mixer.music.play(-1)


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


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def stop(self):
        self.cap.release()

    def run(self):
        self.cap = cv2.VideoCapture(0)
        # mpDraw = mp.solutions.drawing_utils
        mpPose = mp.solutions.pose
        pose = mpPose.Pose()
        # pTime = 0
        start = 0
        count = 0
        while True:
            try:
                ret, frame = self.cap.read()
                result = pose.process(frame)

                if result.pose_landmarks:
                    cv2.imwrite("temp.jpg", frame)

                    try: previous_x_cord, previous_y_cord = extract_cordinates(img="temp.jpg")
                    except Exception: pass

                    # mpDraw.draw_landmarks(frame, result.pose_landmarks, mpPose.POSE_CONNECTIONS)
                    current_x_cord = list()
                    current_y_cord = list()

                    for id, lm in enumerate(result.pose_landmarks.landmark):
                        h, w, c = frame.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)

                        current_x_cord.append(cx)
                        current_y_cord.append(cy)

                    with open('x_cordinates.csv', 'a', encoding='UTF8') as f:
                        writer = csv.writer(f) 
                        writer.writerow(current_x_cord)
                    
                    with open('y_cordinates.csv', 'a', encoding='UTF8') as f:
                        writer = csv.writer(f) 
                        writer.writerow(current_y_cord)

                    pt1, pt2 = bounding_box_cordinates(x_cord_list=current_x_cord, y_cord_list=current_y_cord)


                    if check_movement_range(list1=previous_x_cord, list2=current_x_cord) or check_movement_range(list1=previous_y_cord, list2=current_y_cord):
                        if count < 10:
                            movement_detected_sound()
                        if count > 10:
                            gun_shoot_sound()
                        pt1, pt2 = bounding_box_cordinates(x_cord_list=current_x_cord, y_cord_list=current_y_cord)

                        cv2.rectangle(frame, pt1, pt2, (0,0,255), 6)
                        cv2.putText(frame, " MOTION DETECTED!", (int(pt1[0]),int(pt2[1]/2)), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,255), 4)

                        count += 1

                    else: cv2.rectangle(frame, pt1, pt2, (0,255,0), 3)

            except AttributeError: pass
            except Exception as error: pass
            except UnboundLocalError: pass

            #     cTime = time.time()
            #     fps = 1 / (cTime - pTime)
            #     pTime = cTime

            # cv2.putText(frame, "FPS: {}".format(str(int(fps))), (20,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,153), 2)

            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, ch = rgbImage.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
            p = convertToQtFormat.scaled(5420, 1080, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)


class App(QMainWindow):
    
    def __init__(self):
        super().__init__()

        self.title = 'Red Light, Green Light'
        self.left = 0
        self.top = 0
        self.width = 1920
        self.height = 1080
        self.initUI()

        self.run = 0

    def initUI(self):

        theme_sound()

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.label = QLabel(self)
        self.pixmap = QPixmap('images/background.jpg')
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.pixmap.width(),
                          self.pixmap.height())

        self.start_button = QPushButton("", self)
        self.start_button.setGeometry(100,300,299,99)
        self.start_button.setStyleSheet("background-image : url(images/play.png); border : 0px solid black")
        self.start_button.clicked.connect(self.start_game)

        self.quit_button = QPushButton("", self)
        self.quit_button.setGeometry(100,410,299,99)
        self.quit_button.setStyleSheet("background-image : url(images/quit.png); border : 0px solid black")
        self.quit_button.clicked.connect(self.close)

        self.red_light = QLabel(self)
        self.pixmap = QPixmap('images/red-light.jpg')
        self.red_light.setPixmap(self.pixmap)
        self.red_light.resize(self.pixmap.width(),
                          self.pixmap.height())
        self.red_light.move(60,140)

        self.red_light.setHidden(True)

        self.show()

    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def start_game(self):

        self.setStyleSheet("background-color: lightblue;")

        click_sound()

        loop = QtCore.QEventLoop()

        self.start_button.setHidden(True)
        self.quit_button.setHidden(True)
        self.label.setHidden(True)

        self.green_light = QLabel(self)        
        self.pixmap = QPixmap('images/green-light.jpg')
        self.green_light.setPixmap(self.pixmap)
        self.green_light.resize(self.pixmap.width(),
                          self.pixmap.height())
        self.green_light.move(0,0)
        self.green_light.setHidden(False)

        QtCore.QTimer.singleShot(2000, loop.quit)
        loop.exec_()

        red_light_sound()

        QtCore.QTimer.singleShot(5000, loop.quit)
        loop.exec_()

        turning_sound()

        QtCore.QTimer.singleShot(1000, loop.quit)
        loop.exec_()

        self.green_light.setHidden(True)

        self.label = QLabel(self)
        self.label.move(850,80)
        self.label.resize(1000,800)
        self.pixmap = QPixmap('images/transparent.png')
        self.label.setPixmap(self.pixmap)
        self.label.setHidden(False)

        self.red_light.setHidden(False)
        
        self.camera = QLabel(self)
        self.camera.move(850, 80)
        self.camera.resize(5420, 1080)

        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()

        scanning_sound()

        QtCore.QTimer.singleShot(7000, loop.quit)
        loop.exec_()

        th.stop()

        self.red_light.setHidden(True)

        self.label.setHidden(True)

        self.run += 1

        self.start_game()


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())