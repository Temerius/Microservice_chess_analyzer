import requests
import os
import cv2
from config import FIGURES


def download_bg(style: str):
    start_bg_url = "https://images.chesscomfiles.com/chess-themes/backgrounds/originals/large/"
    mid_bg_url = ".png"
    save_dir = './images/'
    url = start_bg_url + style + mid_bg_url

    try:
        response = requests.get(url)
        response.raise_for_status()

        filename = os.path.join(save_dir, f'bg_{style}.png')

        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f"Downloaded {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")


def download_board(style: str):
    start_boards_url = "https://images.chesscomfiles.com/chess-themes/boards/"
    mid_boards_url = "/200.png"
    save_dir = './images/'
    url = start_boards_url + style + mid_boards_url

    try:
        response = requests.get(url)
        response.raise_for_status()

        filename = os.path.join(save_dir, f'board_{style}.png')

        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f"Downloaded {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")


def download_figures(style: str):
    start_figures_url = "https://images.chesscomfiles.com/chess-themes/pieces/"
    mid_figures_url = "/150/"
    png_figures_list = FIGURES
    save_dir = f'./images/chess_pieces_{style}'
    url = start_figures_url + style + mid_figures_url

    image_urls = [url + i for i in png_figures_list]
    os.makedirs(save_dir, exist_ok=True)

    for url in image_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()

            filename = os.path.join(save_dir, url.split('/')[-1])

            with open(filename, 'wb') as file:
                file.write(response.content)

            print(f"Downloaded {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to download {url}: {e}")


def cut_image(src, style):
    img = cv2.imread(src)
    size = img.shape[0] // 8
    white_cell = img[:size, :size]
    black_cell = img[size: 2 * size, :size]

    for file in os.listdir(f'./images/'):
        if file[6:6 + 4] == 'cell':
            os.remove(f'./images/{file}')

    cv2.imwrite(f'./images/black_cell_{style}.png', black_cell)
    cv2.imwrite(f'./images/white_cell_{style}.png', white_cell)


def download_figure_style(figure_style):
    if not os.path.exists(f'./images/chess_pieces_{figure_style}'):
        for file in os.listdir(f'./images/'):
            if os.path.isdir(f'./images/{file}'):
                for image in os.listdir(f'./images/{file}'):
                    os.remove(f'./images/{file}/{image}')
                os.rmdir(f'./images/{file}')
        download_figures(figure_style)


def download_board_style(board_style):
    if not os.path.exists(f'./images/board_{board_style}.png'):
        for file in os.listdir(f'./images/'):
            if file[:5] == 'board':
                os.remove(f'./images/{file}')
        download_board(board_style)
        cut_image(f'./images/board_{board_style}.png', board_style)


def download_bg_style(bg_style, page):
    if not os.path.exists(f'./images/bg_{bg_style}.png'):
        for file in os.listdir(f'./images/'):
            if file[:2] == 'bg':
                os.remove(f'./images/{file}')
        download_bg(bg_style)
        bg_img = cv2.imread(f'images/bg_{bg_style}.png')
        cv2.resize(bg_img, (int(page.window_width), int(page.window_height)))
        cv2.imwrite(f'images/bg_{bg_style}.png', bg_img)
