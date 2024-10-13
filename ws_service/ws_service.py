import asyncio
import pika
import websockets
import threading

RABBITMQ_HOST = '192.168.206.120'
RABBITMQ_USER = 'lord_temerius'
RABBITMQ_PASSWORD = '0476'
RABBITMQ_VHOST = 'riat'
WS_HOST = '192.168.206.120'
WS_PORT = 54322

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
connection_params = pika.ConnectionParameters(host=RABBITMQ_HOST, virtual_host=RABBITMQ_VHOST, credentials=credentials,
                                              port=5672)

current_chess_board = None


def rabbitmq_listener():
    global current_chess_board

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    channel.queue_declare(queue='chess_positions')

    def callback(ch, method, properties, body):
        global current_chess_board
        current_chess_board = body
        print("Received new chess position data.")

    channel.basic_consume(queue='chess_positions', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


rabbitmq_thread = threading.Thread(target=rabbitmq_listener)
rabbitmq_thread.start()


async def websocket_handler(websocket, path):
    print("Client connected.")
    try:
        while True:
            if current_chess_board:
                await websocket.send(current_chess_board)
                print("Sent chess board data to client.")
            await asyncio.sleep(1)
    except websockets.ConnectionClosed:
        print("Client disconnected.")


async def start_websocket_server():
    async with websockets.serve(websocket_handler, WS_HOST, WS_PORT):
        await asyncio.Future()


asyncio.run(start_websocket_server())
