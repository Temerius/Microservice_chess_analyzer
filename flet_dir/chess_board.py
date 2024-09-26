import flet as ft
from config import FIGURES_PATH

def create_squares(color, size, style):
    src = f'./images/black_cell_{style}.png' if color == 'black' else f'./images/white_cell_{style}.png'
    return ft.Image(
        src=src,
        width=size,
        height=size,
    )


def create_piece(figure_number, size, style):
    image_path = f'./images/chess_pieces_{style}/{FIGURES_PATH[figure_number][1]}'
    size *= 2
    return ft.Image(
        src=image_path,
        width=size,
        height=size,
    )


def create_chess_board(styles: tuple, page: ft.Page, chess_board):
    square_size = page.window_height // 9
    board_size = 8

    if len(chess_board) <= 1:
        chess_board = [[20 for _ in range(board_size)] for _ in range(board_size)]
    else:
        chess_board = [[chess_board[i*8+j] for j in range(board_size)] for i in range(board_size)]
    # board_state[6][0] = f'./images/chess_pieces_{styles[0]}/wr.png'

    board = ft.GridView(
        width=square_size * board_size,
        height=square_size * board_size,
        runs_count=board_size,
        spacing=0,
        run_spacing=0
    )

    board_controls = []

    for row in range(board_size):
        row_controls = []
        for col in range(board_size):
            color = "white" if (row + col) % 2 == 0 else "black"
            square = create_squares(color, square_size, styles[1])

            if chess_board[row][col] != 20:
                piece = create_piece(chess_board[row][col], square_size, styles[0])
                square = ft.Stack(
                    [square, piece],
                    alignment=ft.alignment.Alignment(0, 0)
                )

            cell = ft.Container(
                content=square,
                width=square_size,
                height=square_size
            )

            board.controls.append(cell)
            row_controls.append(cell)

        board_controls.append(row_controls)

    letters = [chr(ord('a') + i) for i in range(board_size)]
    numbers = [str(board_size - i) for i in range(board_size)]

    letter_row_bottom = ft.Row(
        [ft.Container(ft.Text(letter), width=square_size, alignment=ft.alignment.center) for letter in letters],
        spacing=0
    )

    number_column = ft.Column(
        [ft.Container(ft.Text(number), height=square_size, alignment=ft.alignment.center) for number in numbers],
        spacing=0
    )

    board_with_labels = ft.Row(
        [
            number_column,
            board,
        ],
        spacing=10
    )

    return ft.Column(
        [
            board_with_labels,
            letter_row_bottom
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0
    )
