import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume



cap = cv2.VideoCapture(0)
#address = "http://192.168.0.100:8080/video"
#cap.open(address)

pTime = 0

detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
volumeRangeToInterpret = [50, 300]

minBright = 20
maxBright = 100
bright = sbc.get_brightness()
initialBright = bright
prevBright = bright
brightBar = 175
circleSize = 15
brightRangeToInterpret = [200, 550]

barRange = [400,150]

wristLandmark = 0
thumbTipLandmark = 4
indexFingerTipLandmark = 8
pinkyTipLandmark = 20

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:

        x1, y1 = lmList[thumbTipLandmark][1], lmList[thumbTipLandmark][2]
        x2, y2 = lmList[indexFingerTipLandmark][1], lmList[indexFingerTipLandmark][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        x3, y3 = lmList[wristLandmark][1], lmList[wristLandmark][2]
        x4, y4 = lmList[pinkyTipLandmark][1], lmList[pinkyTipLandmark][2]
        cx2, cy2 = (x3 + x4) // 2, (y3 + y4) // 2

        cv2.circle(img, (x1, y1), circleSize, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), circleSize, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), circleSize, (255, 0, 255), cv2.FILLED)

        cv2.circle(img, (x3, y3), circleSize, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x4, y4), circleSize, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x3, y3), (x4, y4), (255, 0, 0), 3)
        cv2.circle(img, (cx2, cy2), circleSize, (255, 0, 0), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        length2 = math.hypot(x4 - x3, y4 - y3)

        vol = np.interp(length, volumeRangeToInterpret, [minVol, maxVol])
        volBar = np.interp(length, volumeRangeToInterpret, barRange)
        volPer = np.interp(length, volumeRangeToInterpret, [0, 100])
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), circleSize, (0, 255, 0), cv2.FILLED)

        bright = np.interp(length2, brightRangeToInterpret, [minBright, maxBright])
        brightBar = np.interp(length2, brightRangeToInterpret, barRange)
        if abs(prevBright-bright) > 5:
            sbc.set_brightness(float(bright))
        prevBright = bright

    img = cv2.resize(img, (0, 0), fx=0.6, fy=0.6)
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 255), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 255), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 3)
    cv2.putText(img, 'volume', (20, 500), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 3)

    cv2.rectangle(img, (1000, 150), (1035, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (1000, int(brightBar)), (1035, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(bright)} %', (990, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cv2.putText(img, 'brightness', (940, 500), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

sbc.set_brightness(initialBright)