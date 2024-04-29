import cv2
import mediapipe as mp
import csv
import math

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

cap = cv2.VideoCapture(3)
pTime = 0

def distance(a, b):
    
    return math.sqrt(math.pow((b[0]-a[0]),2)+math.pow(b[1]-a[1],2))


def extract_cordinates(img):
    image = cv2.imread(img)
    imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = pose.process(imgRGB)
    x_cordinate = list()
    y_cordinate = list()
    if result.pose_landmarks:
        for id, lm in enumerate(result.pose_landmarks.landmark):
            h, w, c = image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            x_cordinate.append(cx)
            y_cordinate.append(cy)
        return x_cordinate, y_cordinate


def check_movement_range(list1, list2):
    # Nose
    # if list1[0] - list2[0] not in range(-8,9):
    #     print("nose") 
    #     return True

    # Shoulder
    # elif list1[11] - list2[11] not in range(-8,8):
    #     print("shoulder") 
    #     return True
    # elif list1[12] - list2[12] not in range(-8,8):
    #     print("shoulder") 
    #     return True
    
    # Wrist
    if list1[15] - list2[15] not in range(-10,11):
        # print("wrist: {}".format(list1[15]-list2[15])) 
        return True
    elif list1[16] - list2[16] not in range(-10,11): 
        # print("wrist: {}".format(list1[16]-list2[16]))
        return True
    
    # Hip
    # elif list1[23] - list2[23] not in range(-15,15):
    #     print("hip") 
    #     return True
    # elif list1[24] - list2[24] not in range(-15,15):
    #     print("hip") 
    #     return True

    # Knee
    elif list1[25] - list2[25] not in range(-20,21): 
        # print('knee: {}'.format(list1[25]-list2[25]))
        return True
    elif list1[26] - list2[26] not in range(-20,21):
        # print('knee: {}'.format(list1[26]-list2[26])) 
        return True

    # Ankle
    # elif list1[27] - list2[27] not in range(-25,25): 
    #     print('ankle')
    #     return True
    # elif list1[28] - list2[28] not in range(-25,25): 
    #     print('ankle')
    #     return True


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


# while True:
  
#     ret, frame = cap.read()
#     frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     result = pose.process(frameRGB)
#     # print(result.pose_landmarks)

#     if result.pose_landmarks:

#         cv2.imwrite("temp.jpg", frame)
#         try:
#             previous_x_cord, previous_y_cord = extract_cordinates(img="temp.jpg")
#         except Exception:
#             pass
#         # print("Previous:")
#         # print(previous_x_cord)
#         # print(previous_y_cord)

#         # mpDraw.draw_landmarks(frame, result.pose_landmarks, mpPose.POSE_CONNECTIONS)
        
#         current_x_cord = list()
#         current_y_cord = list()

#         for id, lm in enumerate(result.pose_landmarks.landmark):
#             h, w, c = frame.shape
#             cx, cy = int(lm.x * w), int(lm.y * h)

#             current_x_cord.append(cx)
#             current_y_cord.append(cy)

#         # print("Current:")
#         # print(current_x_cord)
#         # print(current_y_cord)

#         # with open('x_cordinates.csv', 'a', encoding='UTF8') as f:
#         #     writer = csv.writer(f) 
#         #     writer.writerow(current_x_cord)
        
#         # with open('y_cordinates.csv', 'a', encoding='UTF8') as f:
#         #     writer = csv.writer(f) 
#         #     writer.writerow(current_y_cord)

#         pt1, pt2 = bounding_box_cordinates(x_cord_list=current_x_cord, y_cord_list=current_y_cord)

#         cv2.rectangle(frame, pt1, pt2, (0,255,0), 3)

#         if check_movement_range(list1=previous_x_cord, list2=current_x_cord) or check_movement_range(list1=previous_y_cord, list2=current_y_cord):
#             pt1, pt2 = bounding_box_cordinates(x_cord_list=current_x_cord, y_cord_list=current_y_cord)
#             cv2.rectangle(frame, pt1, pt2, (0,0,255), 5)
            

#     cTime = time.time()
#     fps = 1 / (cTime - pTime)
#     pTime = cTime

#     cv2.putText(frame, "FPS: {}".format(str(int(fps))), (20,30), cv2.FONT_HERSHEY_PLAIN, 2, (0,0,153), 2)

#     cv2.imshow("Movement Detector", frame)

#     if cv2.waitKey(1) == 27:
#         break

# cv2.destroyAllWindows()
# cap.release()
