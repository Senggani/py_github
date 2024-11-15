import requests
from datetime import datetime
import cv2 as cv
import time
import pika

path = "./image/"

# Menyalakan kamera
cap = cv.VideoCapture(0)
if not cap.isOpened():
	print("Camera not detected")
	exit()

while True:
  # Mendapatkan waktu saat ini sebagai penamaan file
  current_datetime = datetime.now()
  formatted_date = current_datetime.strftime("%Y%m%d_%H%M%S")
  fullPath = (path + formatted_date + ".jpg")

  # Mengambil gambar
  ret, image = cap.read()
  if not ret:
    print("error to capture image")

  # Menyimpan Gambar
  cv.imwrite(fullPath, image)
  print(fullPath)

  #=============    OpenCV    =============#
  gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

  face_classifier = cv.CascadeClassifier("haarcascade_frontalface_default.xml")

  face = face_classifier.detectMultiScale(
    gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
  )

  for (x, y, w, h) in face:
    cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 10)
      
  cv.imwrite(fullPath,  image)
  #-------------    OpenCV    -------------#

  #============= RMQ Produce  =============#
  credentials = pika.PlainCredentials('raspi', 'raspi')
  connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.100', 5672, '/', credentials))
  channel = connection.channel()

  channel.queue_declare(queue='opencv_status')

  channel.basic_publish(exchange='',
                        routing_key='opencv_status',
                        body=fullPath)
  print(" [x] Sent: " + fullPath)

  connection.close()
  #------------- RMQ Produce  -------------#

  # Delay untuk pengambilan gambar selanjutnya
  time.sleep(30)

# Mematikan kamera
cap.release

