import socket
import pika
import numpy as np
import cv2

UDP_HOST = '192.168.206.120'
UDP_PORT = 12345
RABBITMQ_HOST = '192.168.206.120'
RABBITMQ_USER = 'lord_temerius'
RABBITMQ_PASSWORD = '0476'
RABBITMQ_VHOST = 'riat'

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
connection_params = pika.ConnectionParameters(host=RABBITMQ_HOST, virtual_host=RABBITMQ_VHOST, credentials=credentials, port=5672)

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
channel.queue_declare(queue='image_queue')

frame_fragments = {}
latest_timestamp = 0


def udp_server():
    global latest_timestamp
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((UDP_HOST, UDP_PORT))
        print(f"UDP server listening on port {UDP_PORT}")
        while True:
            data, addr = s.recvfrom(65507)
            timestamp = int.from_bytes(data[0:8], byteorder='big')
            fragment_number = data[8]
            fragment_data = data[9:]
            if timestamp > latest_timestamp:
                latest_timestamp = timestamp
                frame_fragments.clear()
            if timestamp == latest_timestamp:
                if timestamp not in frame_fragments:
                    frame_fragments[timestamp] = {}
                frame_fragments[timestamp][fragment_number] = fragment_data
                if len(frame_fragments[timestamp]) == 25:
                    print("ready img")
                    image = process_frame(timestamp)

                    channel.basic_publish(exchange='', routing_key='image_queue', body=image.tobytes())


def process_frame(timestamp):
    frame_data = [frame_fragments[timestamp][i] for i in range(25)]
    if len(frame_data) < 25:
        return
    decoded_frames = [cv2.imdecode(np.frombuffer(fragment, np.uint8), cv2.IMREAD_COLOR) for fragment in frame_data]
    if all(frame is not None for frame in decoded_frames):
        rows = [np.concatenate(decoded_frames[i::5], axis=1) for i in range(5)]
        return np.concatenate(rows, axis=0)


if __name__ == "__main__":
    udp_server()
