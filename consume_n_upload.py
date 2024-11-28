import requests, pika, sys, os, json
from datetime import datetime

current_datetime = datetime.now()
formatted_date = current_datetime.strftime("%Y%m%d_%H%M%S")
ip_addr = '192.168.0.104:3000'

def main():
    credentials = pika.PlainCredentials(username='pm_modue', password='hl6GjO5LlRuQT1n')
    connection = pika.BlockingConnection(pika.ConnectionParameters('rmq2.pptik.id', 5672, '/pm_module', credentials))
    channel = connection.channel()

    channel.queue_declare(queue='opencv_retrieve')

    def callback(ch, method, properties, body):
        
        json_str = json.loads(body)
        
        print(f" [x] Received {body}")
        #=============  API Upload  =============#
        url = 'http://'+ip_addr+'/ftp/upload-image'

        with open(json_str['full_path'], 'rb') as image_file:
            files = {'file': (json_str['full_path'], image_file, 'image/jpeg')}
            data = {'name': formatted_date, 'source': 'opencv', 'created_by': 'opencv', 'total_face': json_str['total_face'], 'total_body': json_str['total_body']}
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
