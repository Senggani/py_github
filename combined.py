from datetime import datetime
import cv2 as cv
import time
import requests, pika, sys, os

ip_addr = '192.168.0.104'
path = "./image/"
count = 30
  
credentials = pika.PlainCredentials('raspi', 'raspi')
connection = pika.BlockingConnection(pika.ConnectionParameters(ip_addr, 5672, '/', credentials))

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

  if (count ==  30):
    count = 0
    
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
    channel_detect = connection.channel()

    channel_detect.queue_declare(queue='opencv_status')

    channel_detect.basic_publish(exchange='',
                          routing_key='opencv_status',
                          body=fullPath)
    print(" [x] Sent: " + fullPath)

    connection.close()
    #------------- RMQ Produce  -------------#

  #============= RMQ Consume  =============#
  channel_upload = connection.channel()

  channel_upload.queue_declare(queue='opencv_retrieve')

  def callback(ch, method, properties, body):
    print(f" [x] Received {body}")
    #=============  API Upload  =============#
    url = 'http://'+ip_addr+':3000/ftp/upload-image'

    with open(body, 'rb') as image_file:
      files = {'file': (body, image_file, 'image/jpeg')}
      data = {'name': formatted_date, 'source': 'opencv', 'created_by': 'opencv'}
      response = requests.post(url, files=files, data=data)

    if response.status_code == 200:
      print('File uploaded successfully!')
      print(response.json()) 
    else:
      print(f'Error uploading file: {response.status_code}')
      print(response.text)
    #-------------  API Upload  -------------#

  channel_upload.basic_consume(queue='opencv_retrieve', on_message_callback=callback, auto_ack=True)

  print(' [*] Waiting for messages. To exit press CTRL+C')
  channel_upload.start_consuming()
  #------------- RMQ Consume  -------------#

  # Delay untuk pengambilan gambar selanjutnya
  count = count + 1
  time.sleep(1)

# Mematikan kamera
cap.release

