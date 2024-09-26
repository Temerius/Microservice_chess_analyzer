import flet as ft
import time
import hashlib
import requests
from screeninfo import get_monitors
from threading import Thread, Event
import logging.config
from logging import getLogger
import websocket
import queue
import json
from chess_board import create_chess_board
from setting_window import open_settings_panel
from download import download_board_style, download_figure_style, download_bg_style
import numpy as np


class User:
    def __init__(self, username, password, styles):
        self.name = username
        self.password = password
        self.figure_style = styles[0]
        self.board_style = styles[1]
        self.bg_style = styles[2]
        self.port = 54321
        self.ip = '192.168.43.120'


USER = User('admin', 'password', ['basis', 'green', 'marble'])

CHESS_BOARD = []
with open('client_logging.conf') as f:
    config = json.load(f)

logging.config.dictConfig(config)
logger = getLogger(__name__)

error_queue = queue.Queue()
connection_event = Event()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def get_screen_size():
    monitor = get_monitors()[0]
    width = monitor.width
    height = monitor.height
    return height, width


def main(page: ft.Page):
    page.title = "Chess Analyzer"
    page.theme_mode = 'dark'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window_height, page.window_width = get_screen_size()
    page.window_min_width = 350
    page.window_min_height = 400

    def show_message(message):
        page.snack_bar = ft.SnackBar(content=ft.Text(message))
        page.snack_bar.open = True
        page.update()

    def on_register_click(e):
        global USER
        username = username_input.value
        password = password_input.value
        response = requests.post(f"http://{server_address_input.value}:{server_port_input.value}/register",
                                 json={"username": username, "password": hash_password(password)})

        show_message(response.json().get('msg'))

        styles = response.json()["styles"]
        if styles:
            USER.name = username
            USER.password = password
            USER.figure_style = styles[0]
            USER.board_style = styles[1]
            USER.bg_style = styles[2]
            time.sleep(0.5)
            navigate_to_board(styles)

    def on_login_click(e):
        username = username_input.value
        password = password_input.value
        response = requests.post(f"http://{server_address_input.value}:{server_port_input.value}/login",
                                 json={"username": username, "password": hash_password(password)})
        show_message(response.json().get('msg'))

        styles = response.json()["styles"]
        if styles:
            USER.name = username
            USER.password = password
            USER.figure_style = styles[0]
            USER.board_style = styles[1]
            USER.bg_style = styles[2]
            time.sleep(0.5)
            navigate_to_board(styles)

    def validate(e):
        if all([username_input.value, password_input.value]):
            register_button.disabled = False
            login_button.disabled = False
        else:
            register_button.disabled = True
            login_button.disabled = True
        page.update()

    def create_main_game_panel(username, settings_button):
        page.clean()
        page.navigation_bar = None
        page.bgcolor = ft.colors.TRANSPARENT

        board_panel = create_chess_board((USER.figure_style, USER.board_style), page, CHESS_BOARD)
        main_game_panel = ft.Container(
            content=ft.Row(
                [
                    board_panel,
                    ft.Row(
                        [
                            username,
                            settings_button
                        ],
                        alignment=ft.alignment.top_right,
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START
            ),

            expand=True,
            alignment=ft.alignment.center,
            bgcolor=ft.colors.TRANSPARENT,
            image_src=f'./images/bg_{USER.bg_style}.png',
            image_fit=ft.ImageFit.COVER
        )

        return main_game_panel

    def navigate_to_board(styles: tuple):

        def call_setting_panel(e):

            def change_username(new_username):
                response = requests.post(f"http://{server_address_input.value}:{server_port_input.value}/change_name",
                                         json={"new_name": new_username, "old_name": USER.name})
                show_message(response.json().get('msg'))

                success = response.json()["success"]

                if success:
                    USER.name = new_username
                    username_text.value = new_username
                    page.update()

            def change_password(new_password: str):
                response = requests.post(f"http://{server_address_input.value}:{server_port_input.value}/change_pwd",
                                         json={"new_pwd": hash_password(new_password), "name": USER.name})
                show_message(response.json().get('msg'))

                success = response.json()["success"]

                if success:
                    USER.password = new_password

            def change_figure_style(new_style: str):
                response = requests.post(
                    f"http://{server_address_input.value}:{server_port_input.value}/change_figure_style",
                    json={"new_style": new_style, "name": USER.name})
                show_message(response.json().get('msg'))

                success = response.json()["success"]

                if success:
                    USER.figure_style = new_style
                    download_figure_style(new_style)
                    page.controls[0].content.controls[0] = create_chess_board((USER.figure_style, USER.board_style),
                                                                              page, CHESS_BOARD)
                    page.update()

            def change_board_style(new_style: str):
                response = requests.post(
                    f"http://{server_address_input.value}:{server_port_input.value}/change_board_style",
                    json={"new_style": new_style, "name": USER.name})
                show_message(response.json().get('msg'))

                success = response.json()["success"]

                if success:
                    USER.board_style = new_style
                    download_board_style(new_style)
                    page.controls[0].content.controls[0] = create_chess_board((USER.figure_style, USER.board_style),
                                                                              page, CHESS_BOARD)
                    page.update()

            def change_bg_style(new_style: str):
                response = requests.post(
                    f"http://{server_address_input.value}:{server_port_input.value}/change_bg_style",
                    json={"new_style": new_style, "name": USER.name})
                show_message(response.json().get('msg'))

                success = response.json()["success"]

                if success:
                    USER.bg_style = new_style
                    download_bg_style(new_style, page)
                    page.controls[0].image_src = f"./images/bg_{USER.bg_style}.png"
                    page.update()
                    #page.add(create_main_game_panel(username_text, settings_button))

            changes = {
                'username': change_username,
                'password': change_password,
                'figure_style': change_figure_style,
                'board_style': change_board_style,
                'bg_style': change_bg_style
            }

            def settings_changes(msg, *args):
                print(f'change {msg}: {args}')
                changes[msg](*args)

            open_settings_panel(page, USER, settings_changes)

        settings_button = ft.IconButton(
            icon=ft.icons.SETTINGS,
            on_click=call_setting_panel,
            alignment=ft.alignment.top_right,
            icon_size=40
        )
        username_text = ft.Text(value=USER.name)

        download_figure_style(styles[0])
        download_board_style(styles[1])
        download_bg_style(styles[2], page)

        page.add(create_main_game_panel(username_text, settings_button))

    username_input = ft.TextField(label="Username", width=300, on_change=validate)
    password_input = ft.TextField(label="Password", password=True, can_reveal_password=True, width=300,
                                  on_change=validate)

    register_button = ft.ElevatedButton(text="Register", on_click=on_register_click, disabled=True)
    login_button = ft.ElevatedButton(text="Login", on_click=on_login_click, disabled=True)

    panel_register = ft.Row(
        [
            ft.Column(
                [
                    ft.Text("Registration"),
                    username_input,
                    password_input,
                    register_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    panel_login = ft.Row(
        [
            ft.Column(
                [
                    ft.Text("Authorization"),
                    username_input,
                    password_input,
                    login_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER
    )

    def create_login_register_panel():
        page.clean()
        page.navigation_bar = ft.NavigationBar(
            destinations=[
                ft.NavigationDestination(icon=ft.icons.LOGIN, label="Authorization"),
                ft.NavigationDestination(icon=ft.icons.NEW_LABEL, label="Registration"),
            ],
            on_change=navigate
        )
        page.add(panel_login)

    def on_connect_click(e):
        server_address = server_address_input.value
        server_port = server_port_input.value
        if server_address and server_port:
            logger.info(f'server address: {server_address}:{server_port}')
            success = connect_to_server(server_address, server_port)
            if success:
                show_message("Successfully connected to server")
                create_login_register_panel()
        else:
            show_message("Please enter a valid server address and port.")

    def connect_to_server(address, port):
        url = f"ws://{address}:{int(port) + 1}/ws"
        connection_event.clear()
        logger.info(f'Connecting to server: {url}')
        ws_thread = Thread(target=start_websocket, args=(url,))
        ws_thread.start()
        connection_event.wait()
        logger.info(f'Connection event: {connection_event}')

        if not error_queue.empty():
            error = error_queue.get()
            logger.error(f"Error in WebSocket connection: {error}")
            show_message(f"Error in WebSocket connection: {error}")
            return False
        return True

    def start_websocket(url):
        try:
            def on_message(ws, message):
                CHESS_BOARD = np.frombuffer(message, dtype=np.int32)
                logger.info(f'WebSocket message: {CHESS_BOARD}')
                board_panel = create_chess_board((USER.figure_style, USER.board_style), page, CHESS_BOARD)
                page.controls[0].content.controls[0] = board_panel
                page.update()

            def on_error(ws, error):
                logger.error(f"WebSocket error: {error}")
                error_queue.put(error)
                connection_event.set()

            def on_close(ws, close_status_code, close_msg):
                logger.info(f"WebSocket closed, closed code = {close_status_code}, close_msg = {close_msg}")
                connection_event.set()

            def on_open(ws):
                logger.info("WebSocket connection opened")
                connection_event.set()

            ws = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error, on_close=on_close)
            ws.on_open = on_open
            ws.run_forever()
        except Exception as e:
            error_queue.put(e)
            connection_event.set()

    server_address_input = ft.TextField(label="Server Address", value='192.168.43.120', width=300)
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

    def navigate(e):
        idx = page.navigation_bar.selected_index
        page.clean()

        if idx == 0:
            logger.info('switch to login panel')
            page.add(panel_login)
        elif idx == 1:
            logger.info('switch to register panel')
            page.add(panel_register)

    page.add(connection_panel)


ft.app(target=main)
