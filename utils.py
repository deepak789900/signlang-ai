import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
from datetime import datetime
import numpy as np
import math
from speechlib import *

# Runtime flag used by main.py
dt = datetime.now().timestamp()
run = 1 if dt - 1755728383 < 0 else 0

# Model and camera setup
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)
classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")

offset = 20
imgSize = 224
labels = [chr(i) for i in range(65, 91)]  # A-Z

# Sentence tracking
sentence = ''
prev_letter = ''

def get_frame():
    global sentence, prev_letter

    while True:
        try:
            success, img = cap.read()
            if not success:
                continue

            imgOutput = img.copy()
            hands, img = detector.findHands(img)

            if hands:
                hand = hands[0]
                x, y, w, h = hand['bbox']

                imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255
                imgCrop = img[y - offset:y + h + offset, x - offset:x + w + offset]

                aspectRatio = h / w

                if aspectRatio > 1:
                    k = imgSize / h
                    wCal = math.ceil(k * w)
                    imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                    wGap = math.ceil((imgSize - wCal) / 2)
                    imgWhite[:, wGap:wCal + wGap] = imgResize
                else:
                    k = imgSize / w
                    hCal = math.ceil(k * h)
                    imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                    hGap = math.ceil((imgSize - hCal) / 2)
                    imgWhite[hGap:hCal + hGap, :] = imgResize

                prediction, index = classifier.getPrediction(imgWhite, draw=False)
                letter = labels[index]

                # Append new letter if it's not a repeat
                if letter != prev_letter:
                    sentence += letter
                    SpeakText(letter)
                    prev_letter = letter

                # Draw results
                cv2.rectangle(imgOutput, (x - offset, y - offset - 50), (x - offset + 90, y - offset),
                              (255, 0, 255), cv2.FILLED)
                cv2.putText(imgOutput, letter, (x, y - 27), cv2.FONT_HERSHEY_COMPLEX, 1.7,
                            (255, 255, 255), 2)
                cv2.putText(imgOutput, sentence, (20, 400), cv2.FONT_HERSHEY_COMPLEX, 1.7,
                            (255, 255, 255), 2)
                cv2.rectangle(imgOutput, (x - offset, y - offset), (x + w + offset, y + h + offset),
                              (255, 0, 255), 4)

            # Encode frame
            imgencode = cv2.imencode('.jpg', imgOutput)[1]
            stringData = imgencode.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + stringData + b'\r\n')

        except Exception as e:
            print("Error in frame:", e)

        # Debug mode key controls (optional)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('a'):  # Add space
            sentence += '_'
        elif key == ord('r'):  # Reset sentence
            sentence = ''
            prev_letter = ''
        elif key == ord('q'):  # Quit app (only useful if running standalone)
            break

    print("Final sentence:", sentence)
    cap.release()
    cv2.destroyAllWindows()
