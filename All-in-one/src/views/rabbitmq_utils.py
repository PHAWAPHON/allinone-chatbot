import json
import pika

def send_upload_request(file_path, mime_type, file_name, customer_id):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='file_uploads')

        message = json.dumps({
            'file_path': file_path,
            'mime_type': mime_type,
            'file_name': file_name,
            'customer_id': customer_id
        })

        channel.basic_publish(exchange='', routing_key='file_uploads', body=message)
        print(" [x] Sent upload request for:", file_name)
        connection.close()
    except Exception as e:
        print(f"Error sending upload request: {e}")
