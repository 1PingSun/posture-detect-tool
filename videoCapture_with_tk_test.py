import tkinter as tk
import cv2
from PIL import Image, ImageTk
import time
import mediapipe as mp
import math
import argparse
import matplotlib.pyplot as plt


# 參數調整 ===================================
helpMsg = "參數調整說明：你可以依據自己的需求調整參數，以下是可調整的參數，各式為 python3 videoCapture_with_tk_text.py --parameterName parameterValue"
parser = argparse.ArgumentParser(description=helpMsg)
parser.add_argument('--textSize', type=int, default=2, help="調整文字大小，預設為：2")
parser.add_argument('--textBold', type=int, default=5, help="調整文字粗細，預設為：5")
parser.add_argument('--cameraWidth', type=int, default=1280, help="調整畫面寬度，預設為：1280（單位：px）")
parser.add_argument('--cameraHeight', type=int, default=720, help="調整畫面高度，預設為：720（單位：px）")
parser.add_argument('--detectType', type=int, default=2, help="調整偵測模式，預設為：2（駝背：0，頭前伸：1，高低肩：2，圓肩：3）")
parser.add_argument('--detectSide', type=str, default="L", help="調整偵測方向，預設為：L（左：L，右：R）")
parser.add_argument('--correctDistance', type=int, default=200, help="設定正確姿勢時的距離，預設為：200（單位：px），限駝背及圓肩使用")

args = parser.parse_args()
cameraWidth = args.cameraWidth      # 顯示畫面尺寸（Width）
cameraHeight = args.cameraHeight    # 顯示畫面尺寸（Height）
detectPosture = args.detectType     # 駝背：0，頭前伸：1，高低肩：2，圓肩：3
detectSide = args.detectSide        # 偵測方向
numbersSize = args.textSize         # 數字尺寸
numbersBold = args.textBold         # 數字粗細
correctDistance = args.correctDistance

# ================================ init value ===============================
safeRange = [0,0]
yLim = [0,0]
if(detectPosture==0):
    yLim = [0, 720]
    safeRange = [correctDistance*0.95,720]
elif(detectPosture==1):
    safeRange = [50,90]
    yLim = [0,90]
elif(detectPosture==2):
    safeRange = [-3,3]
    yLim = [-30,30]
elif(detectPosture==3):
    yLim = [0, 720]
    safeRange = [correctDistance*0.95,0]

# ================================ init =====================================
# plot init
def setupPlot():
    global pltCount
    global pltX
    global pltY

    pltCount = 1
    pltX = []
    pltY = []
    plt.cla()
    plt.ion()
    plt.ylim(yLim[0], yLim[1])
    plt.fill_between([0,100], safeRange[0], safeRange[1], color='green', alpha=0.3)
    plt.pause(1)

# Mediapipe init
def setupMediapipe():
    global mp_drawing
    global mp_pose
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

# Tk window init
def setupTk():
    global root
    global cameracanvas
    global inputEntry

    # Create a Tkinter window
    root = tk.Tk()
    root.title("OpenCV with Tkinter")

    # Create a Canvas to display the camera feed
    cameracanvas = tk.Canvas(root, width=cameraWidth, height=cameraHeight)
    cameracanvas.pack()

# read camera init 
def setupCamera():
    global camera

    # Open the camera
    camera = cv2.VideoCapture(0)

# ================================ pose =====================================
# calculate distance
def calculateDistance(a1, a2):
    x = abs(a1[0]-a2[0])
    y = abs(a1[1]-a2[1])
    return math.sqrt(x**2 + y**2)

# calculate angle
def calculateAngle(a1, a2):
    dx = a2[0] - a1[0]
    dy = a2[1] - a1[1]

    # 計算連線與鉛直線的夾角（以弧度為單位）
    angle_radians = math.atan2(dy, dx)

    # 將弧度轉換為角度
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees

# 計算駝背：0
def processKyphosis(a1, a2, image):
    coordinate = [(a1[0] + a1[0]) // 2, (a2[1] + a2[1]) // 2]
    textNum = calculateDistance([a1[0], a1[1]], [a2[0], a2[1]])

    isBad = False
    if(textNum < (correctDistance*0.95)):
        isBad = True
    image = drawLine(isBad, image, a1, a2)
    return textNum, coordinate, image

# 計算頭前伸：1
def processForwardHead(a1, a2, image):
    coordinate = [(a1[0] + a1[0]) // 2, (a2[1] + a2[1]) // 2]
    textNum = 90 - calculateAngle([a2[1], a2[0]], [a1[1], a1[0]])

    isBad = False
    if(textNum < 50):
        isBad = True
    image = drawLine(isBad, image, a1, a2)
    return textNum, coordinate, image

# 計算高低肩：2
def processScoliosis(a1, a2, image):
    coordinate = [(a1[0] + a1[0]) // 2, (a2[1] + a2[1]) // 2]
    textNum = calculateAngle([a2[1], a2[0]], [a1[1], a1[0]]) - 90

    isBad = False
    if(textNum > 3 or textNum < -3):
        isBad = True
    image = drawLine(isBad, image, a1, a2)
    return textNum, coordinate, image

# 計算圓肩：3
def processRoundShoulder(a1, a2, image):
    coordinate = [(a1[0] + a1[0]) // 2, (a2[1] + a2[1]) // 2]
    textNum = calculateDistance([a1[0], a1[1]], [a2[0], a2[1]])

    isBad = False
    if(textNum < (correctDistance*0.95)):
        isBad = True
    image = drawLine(isBad, image, a1, a2)
    return textNum, coordinate, image

# draw line
def drawLine(isBad, image, a1, a2):
    lineColor = (0, 255, 0)
    if(isBad):
        lineColor = (0, 0, 255)
    cv2.line(image, tuple(a1), tuple(a2), lineColor, thickness=20)
    return image

# draw plt
def drawPlt(textNum):
    global pltCount
    global pltX
    global pltY
    pltCount += 1
    if(pltCount >= 100):
        setupPlot()
    pltX.append(pltCount)
    pltY.append(textNum)
    plt.plot(pltX,pltY,"b-o")
    plt.pause(0.05)

# pose reader
def poseReader(image):
    # 偵測人體姿態
    with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
        results = pose.process(image)
    
    if results.pose_landmarks:
        Lshoulder = [int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * cameraWidth), int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * cameraHeight)]
        Rshoulder = [int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * cameraWidth), int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * cameraHeight)]
        Lhip = [int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x * cameraWidth), int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y * cameraHeight)]
        Rhip = [int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].x * cameraWidth), int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y * cameraHeight)]
        Lear = [int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR].x * cameraWidth), int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR].y * cameraHeight)]
        Rear = [int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EAR].x * cameraWidth), int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EAR].y * cameraHeight)]
        
        textNum = 0.0
        coordinate = [0,0]

        if(detectPosture == 0):
            if(detectSide == "L"):
                textNum, coordinate, image = processKyphosis(Lshoulder, Lhip, image)
            else:
                textNum, coordinate, image = processKyphosis(Rshoulder, Rhip, image)
                
        elif(detectPosture == 1):
            if(detectSide == "L"):
                textNum, coordinate, image = processForwardHead(Lshoulder, Lear, image)
            else:
                textNum, coordinate, image = processForwardHead(Rshoulder, Rear, image)

        elif(detectPosture == 2):
            textNum, coordinate, image = processScoliosis(Lshoulder, Rshoulder, image)

        elif(detectPosture == 3):
            textNum, coordinate, image = processRoundShoulder(Lshoulder, Rshoulder, image)

        drawPlt(textNum)
        # 繪製結果
        cv2.putText(image, f'{textNum:.2f}', tuple(coordinate), cv2.FONT_HERSHEY_SIMPLEX, numbersSize, (0, 255, 0), numbersBold) # color with BGR
    return image

# ================================ frame =========================================
# read camera image
def get_frame():
    ret, frame = camera.read()
    frame = cv2.resize(frame, (cameraWidth,cameraHeight), interpolation=cv2.INTER_AREA)
    if ret:
        frame = cv2.flip(frame, 1)
        frame = poseReader(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV uses BGR format, convert it to RGB
        # Convert the frame to ImageTk format
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        show_frame(imgtk)
    cameracanvas.after(10, get_frame)

# show image
def show_frame(imgtk):
    cameracanvas.create_image(0, 0, anchor='nw', image=imgtk)
    cameracanvas.imgtk = imgtk

# ================================ main program ================================
setupTk()
setupPlot()
setupMediapipe()
setupCamera()

# Start displaying the camera feed
get_frame()

# Run the Tkinter event loop
root.mainloop()

# Release the camera when the window is closed
camera.release()