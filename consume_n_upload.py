import requests, pika, sys, os
from datetime import datetime

current_datetime = datetime.now()
formatted_date = current_datetime.strftime("%Y%m%d_%H%M%S")

def main():
    credentials = pika.PlainCredentials('raspi', 'raspi')
    connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.0.106', 5672, '/', credentials))
    channel = connection.channel()

    channel.queue_declare(queue='opencv_retrieve')

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        #=============  API Upload  =============#
        url = 'http://192.168.0.106:3000/ftp/upload-image'

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

    channel.basic_consume(queue='opencv_retrieve', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
