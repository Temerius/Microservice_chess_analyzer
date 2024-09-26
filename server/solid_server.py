import socket
import threading as th
import asyncio
import logging.config
from logging import getLogger
import json
import cv2
import numpy as np
from flask import Flask, request, jsonify
from hypercorn.asyncio import serve
from hypercorn.config import Config
import websockets
from queue import Queue
from digital_figures import digitalization
from sql import init_db, register_user, login_user, change_username, change_password, change_figure_style, \
    change_board_style, change_bg_style

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

with open('server_logging.conf') as f:
    config = json.load(f)

logging.config.dictConfig(config)
logger = getLogger(__name__)

UDP_HOST = '192.168.100.8'
UDP_PORT = 12345
FLASK_PORT = 54321
WS_PORT = 54322

udp_queue = Queue()

frame_fragments = {}
latest_timestamp = 0


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    msg, styles = register_user(username, password)
    return jsonify({'msg': msg, 'styles': styles})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    msg, styles = login_user(username, password)
    return jsonify({'msg': msg, 'styles': styles})


@app.route('/change_name', methods=['POST'])
def chg_name():
    data = request.get_json()
    new_username = data.get('new_name')
    old_username = data.get('old_name')
    success, msg = change_username(new_username, old_username)
    return jsonify({'success': success, 'msg': msg})


@app.route('/change_pwd', methods=['POST'])
def chg_pwd():
    data = request.get_json()
    new_password = data.get('new_pwd')
    username = data.get('name')
    success, msg = change_password(new_password, username)
    return jsonify({'success': success, 'msg': msg})


@app.route('/change_figure_style', methods=['POST'])
def chg_figure_style():
    data = request.get_json()
    new_style = data.get('new_style')
    username = data.get('name')
    success, msg = change_figure_style(new_style, username)
    return jsonify({'success': success, 'msg': msg})


@app.route('/change_board_style', methods=['POST'])
def chg_board_style():
    data = request.get_json()
    new_style = data.get('new_style')
    username = data.get('name')
    success, msg = change_board_style(new_style, username)
    return jsonify({'success': success, 'msg': msg})


@app.route('/change_bg_style', methods=['POST'])
def chg_bg_style():
    data = request.get_json()
    new_style = data.get('new_style')
    username = data.get('name')
    success, msg = change_bg_style(new_style, username)
    return jsonify({'success': success, 'msg': msg})


def udp_server():
    global latest_timestamp
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((UDP_HOST, UDP_PORT))
        print('UDP server listening on port {}'.format(UDP_PORT))
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
                    process_frame(timestamp)


def process_frame(timestamp):
    frame_data = [frame_fragments[timestamp][i] for i in range(25)]
    if len(frame_data) < 25:
        return
    decoded_frames = [cv2.imdecode(np.frombuffer(fragment, np.uint8), cv2.IMREAD_COLOR) for fragment in frame_data]
    if all(frame is not None for frame in decoded_frames):
        rows = [np.concatenate(decoded_frames[i::5], axis=1) for i in range(5)]
        frame = np.concatenate(rows, axis=0)

        logger.info('getting chess arr from digitalization')
        chess_arr = digitalization(frame)

        if chess_arr is None:
            return
        logger.info('got chess arr from digitalization')
        logger.info(chess_arr)
        logger.info('putting chess arr into queue')
        udp_queue.put(chess_arr.tobytes())


async def websocket_handler(websocket, path):
    logger.info("Client connected")
    try:
        while True:
            if not udp_queue.empty():
                data = udp_queue.get()
                logger.info('sending data')
                await websocket.send(data)
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info("Client disconnected")


async def start_websocket_server():
    async with websockets.serve(websocket_handler, UDP_HOST, WS_PORT):
        await asyncio.Future()


async def main():
    try:
        config = Config()
        config.bind = [f"{UDP_HOST}:{FLASK_PORT}"]

        udp_thread = th.Thread(target=udp_server, daemon=True)
        udp_thread.start()

        flask_task = serve(app, config)
        websocket_task = start_websocket_server()

        await asyncio.gather(flask_task, websocket_task)
    except Exception as e:
        logger.critical(e)


init_db()
asyncio.run(main())
