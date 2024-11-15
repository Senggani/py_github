import cv2 as cv
import time
from datetime import datetime

path = "./new_image/"

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
	
	# Delay untuk pengambilan gambar selanjutnya
	time.sleep(30)

# Mematikan kamera
cap.release
