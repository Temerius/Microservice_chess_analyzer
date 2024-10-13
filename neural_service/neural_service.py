import pika
import numpy as np
import digital_figures

RABBITMQ_HOST = '192.168.206.120'
RABBITMQ_USER = 'lord_temerius'
RABBITMQ_PASSWORD = '0476'
RABBITMQ_VHOST = 'riat'

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
connection_params = pika.ConnectionParameters(host=RABBITMQ_HOST, virtual_host=RABBITMQ_VHOST, credentials=credentials,
                                              port=5672)

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

channel.queue_declare(queue='image_queue')
channel.queue_declare(queue='chess_positions')


def process_image(ch, method, properties, body):
    frame = np.frombuffer(body, dtype=np.uint8).reshape(640, 640, 3)

    chess_board = digital_figures.digitalization(frame)

    if chess_board is not None:
        channel.basic_publish(exchange='', routing_key='chess_positions', body=chess_board.tobytes())
        print("Processed and sent chess position data to chess_positions queue.")

    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue='image_queue', on_message_callback=process_image, auto_ack=False)
print("Waiting for messages in image_queue...")
channel.start_consuming()
