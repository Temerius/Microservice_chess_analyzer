import flet as ft
from threading import Thread
import logging.config
from logging import getLogger
import websocket
import requests
import json

with open('client_logging.conf') as f:
    config = json.load(f)

logging.config.dictConfig(config)
logger = getLogger(__name__)
# FORMAT = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
# file_handler = FileHandler('client.log')
# file_handler.setLevel(DEBUG)
# console = StreamHandler()
# console.setLevel(ERROR)
# basicConfig(level=INFO, format=FORMAT, handlers=[file_handler, console])

def main(page: ft.Page):
    page.title = "Chess Analyzer"
    page.theme_mode = 'dark'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_min_width = 350
    page.window_min_height = 400

    def on_connect_click(e):
        server_address = server_address_input.value
        server_port = server_port_input.value
        if server_address and server_port:
            connect_to_server(server_address, server_port)
            page.add(create_login_register_panel())
        else:
            show_message("Please enter a valid server address and port.")

    def connect_to_server(address, port):
        url = f"ws://{address}:{port}/ws"
        ws_thread = Thread(target=start_websocket, args=(url,))
        ws_thread.start()

    def start_websocket(url):
        def on_message(ws, message):
            # Handle incoming messages from the server
            pass

        def socket_error(ws, error):
            logger.error(f"WebSocket error: {error}")

        def close_socket(ws, close_code, close_msg):
            logger.info("WebSocket closed")

        def open_socket(ws):
            logger.info("WebSocket connection opened")

        ws = websocket.WebSocketApp(url, on_message=on_message, on_error=socket_error, on_close=close_socket)
        ws.on_open = open_socket
        ws.run_forever()

    def show_message(message):
        page.snack_bar = ft.SnackBar(content=ft.Text(message))
        page.snack_bar.open = True
        page.update()

    server_address_input = ft.TextField(label="Server Address", value='192.168.100.9',width=300)
    server_port_input = ft.TextField(label="Server Port", value='54321', width=300)
    connect_button = ft.ElevatedButton(text="Connect", on_click=on_connect_click)

    connection_panel = ft.Row(
        [
            ft.Column(
                [
                    ft.Text("Server Connection"),
                    server_address_input,
                    server_port_input,
                    connect_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    def create_login_register_panel():
        def on_register_click(e):
            username = username_input.value
            password = password_input.value
            response = requests.post(f"http://{server_address_input.value}:{server_port_input.value}/register", json={"username": username, "password": password})
            show_message(response.json().get('message'))

        def on_login_click(e):
            username = username_input.value
            password = password_input.value
            response = requests.post(f"http://{server_address_input.value}:{server_port_input.value}/login", json={"username": username, "password": password})
            show_message(response.json().get('message'))

        username_input = ft.TextField(label="Username", width=300)
        password_input = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300)
        register_button = ft.ElevatedButton(text="Register", on_click=on_register_click)
        login_button = ft.ElevatedButton(text="Login", on_click=on_login_click)

        return ft.Row(
            [
                ft.Column(
                    [
                        ft.Text("Authorization"),
                        username_input,
                        password_input,
                        login_button,
                        register_button
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

    page.add(connection_panel)

ft.app(target=main)
