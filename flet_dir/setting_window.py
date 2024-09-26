import flet as ft
import time
from config import FIGURE_STYLES, BOARD_STYLES, BG_STYLES


def open_profile_dialog(page: ft.Page, user, profile_callback):
    def close_dialog(e):
        if user_name.value != user.name:
            profile_callback('username', user_name.value)
        if user_psw.value != user.password:
            profile_callback('password', user_psw.value)
        page.dialog.open = False
        page.update()

    user_name = ft.TextField(label="Name", value=user.name, width=300)
    user_psw = ft.TextField(label="Password", value=user.password, password=True, can_reveal_password=True, width=300)
    dialog = ft.AlertDialog(
        title=ft.Text("Profile Settings"),
        content=ft.Column(
            [
                user_name,
                user_psw,
                ft.ElevatedButton("Save changes", on_click=close_dialog)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        on_dismiss=lambda e: print("Profile dialog dismissed!")
    )
    page.dialog = dialog
    dialog.open = True
    page.update()


def open_theme_dialog(page: ft.Page, user, theme_callback):
    def close_dialog(e):

        if board_style_dropdown.value != user.board_style:
            page.snack_bar = ft.SnackBar(ft.Text(f"Selected board style: {board_style_dropdown.value}"), open=True)
            page.update()
            theme_callback('board_style', board_style_dropdown.value)
        if figure_style_dropdown.value != user.figure_style:
            page.snack_bar = ft.SnackBar(ft.Text(f"Selected figure style: {figure_style_dropdown.value}"), open=True)
            page.update()
            theme_callback('figure_style', figure_style_dropdown.value)
            page.snack_bar = ft.SnackBar(ft.Text(f"Themes was updated"), open=True)

            page.update()
        if bg_style_dropdown.value != user.bg_style:
            page.snack_bar = ft.SnackBar(ft.Text(f"Selected background style: {bg_style_dropdown.value}"), open=True)
            page.update()
            theme_callback('bg_style', bg_style_dropdown.value)

        page.dialog.open = False
        page.update()

    board_styles = BOARD_STYLES
    piece_styles = FIGURE_STYLES
    bg_styles = BG_STYLES

    board_style_dropdown = ft.Dropdown(
        label="Select Board Style",
        options=[ft.dropdown.Option(style) for style in board_styles],
        value=user.board_style,
        text_size=10
    )
    figure_style_dropdown = ft.Dropdown(
        label="Select Piece Style",
        options=[ft.dropdown.Option(style) for style in piece_styles],
        value=user.figure_style,
        text_size=10
    )
    bg_style_dropdown = ft.Dropdown(
        label="Select Background Style",
        options=[ft.dropdown.Option(style) for style in bg_styles],
        value=user.bg_style,
        text_size=10
    )

    dialog = ft.AlertDialog(
        title=ft.Text("Theme Settings"),
        content=ft.Column(
            [
                board_style_dropdown,
                figure_style_dropdown,
                bg_style_dropdown,
                ft.ElevatedButton("Save changes", on_click=close_dialog)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        on_dismiss=lambda e: print("Theme dialog dismissed!")
    )
    page.dialog = dialog
    dialog.open = True
    page.update()


def quit_dialog(page: ft.Page, user, quit_callback):
    pass


def open_server_dialog(page: ft.Page, user, server_callback):
    pass


def open_settings_panel(page: ft.Page, user, callback=None):
    if page.overlay:
        page.overlay.clear()
        page.update()
        return

    panel = ft.Container(
        content=ft.Column(
            [
                ft.TextButton("Profile", on_click=lambda e: open_profile_dialog(page, user, callback)),
                ft.TextButton("Themes", on_click=lambda e: open_theme_dialog(page, user, callback)),
                ft.TextButton("Server", on_click=lambda e: open_server_dialog(page, user, callback)),
                ft.TextButton("Sign out", on_click=lambda e: quit_dialog(page, user, callback)),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        # padding=ft.Padding(10, 10, 10, 10),
        width=150,
        height=200,
        bgcolor=ft.colors.TRANSPARENT,
        border_radius=ft.BorderRadius(10, 0, 10, 0),
        offset=ft.transform.Offset(page.window_width / 150, 0),
        animate_offset=ft.animation.Animation(1000, ft.AnimationCurve('ease')),
    )

    page.overlay.append(panel)
    page.update()
    time.sleep(0.1)
    panel.offset = ft.transform.Offset(page.window_width / panel.width - 1,
                                       page.window_height / panel.height * 0.1)
    page.update()
