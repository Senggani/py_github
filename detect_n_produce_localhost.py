import requests
from datetime import datetime
import cv2 as cv

import pika

imagePath = "C:/Users/hp/Pictures/foto.jpg"
savePath = "./py_github/image/"

current_datetime = datetime.now()

formatted_date = current_datetime.strftime("%Y%m%d_%H%M%S")

fullPath = (savePath + formatted_date + '.jpg')

#=============    OpenCV    =============#
img = cv.imread(imagePath)
gray_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

face_classifier = cv.CascadeClassifier(
    cv.data.haarcascades + "haarcascade_frontalface_default.xml"
)

face = face_classifier.detectMultiScale(
    gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
)

for (x, y, w, h) in face:
    cv.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 20)
    
cv.imwrite(fullPath,  img)
#-------------    OpenCV    -------------#

#============= RMQ Produce  =============#
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='opencv_status')

channel.basic_publish(exchange='',
                      routing_key='opencv_status',
                      body=fullPath)
print(" [x] Sent: " + fullPath)

connection.close()
#------------- RMQ Produce  -------------#
