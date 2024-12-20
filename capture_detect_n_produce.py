from datetime import datetime
import cv2 as cv
import time, pika, json, requests

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

  # Deteksi Wajah
  face_classifier = cv.CascadeClassifier("haarcascade_frontalface_default.xml")

  face = face_classifier.detectMultiScale(
    gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
  )
  
  print("Total detected face = " + str(len(face)))
  
  for (x, y, w, h) in face:
    cv.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 10)
  
  # Deteksi Tubuh
  body_classifier = cv.CascadeClassifier("haarcascade_fullbody.xml")
  
  body = body_classifier.detectMultiScale(
    gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
  )
  
  print("Total detected body = " + str(len(body)))

  for (x, y, w, h) in body:
    cv.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 10)
      
  cv.imwrite(fullPath,  image)
  #-------------    OpenCV    -------------#

  #============= RMQ Produce  =============#
  credentials = pika.PlainCredentials(username='pm_modue', password='hl6GjO5LlRuQT1n')
  connection = pika.BlockingConnection(pika.ConnectionParameters('rmq2.pptik.id', 5672, '/pm_module', credentials))
  channel = connection.channel()

  channel.queue_declare(queue='opencv_status')
  
  message = ('{"full_path": "'+fullPath+'", "total_face": '+str(len(face))+', "total_body": '+str(len(body))+'}')

  channel.basic_publish(exchange='',
                        routing_key='opencv_status',
                        body=message)
  print(" [x] Sent: " + message)

  connection.close()
  #------------- RMQ Produce  -------------#

  # Delay untuk pengambilan gambar selanjutnya
  time.sleep(30)

# Mematikan kamera
cap.release

