import os
import requests

start_boards_url = "https://images.chesscomfiles.com/chess-themes/boards/"
mid_boards_url = "/200.png"
board_style = [
    'green',
    'dark_wood',
    'glass',
    'brown',
    'icy_sea',
    'newspaper',
    'walnut',
    'sky',
    'lolz',
    'stone',
    'bases',
    '8_bit',
    'marble',
    'purple',
    'translucent',
    'metal',
    'tournament',
    'dash',
    'burled_wood',
    'blue',
    'bubblegum',
    'checkers',
    'graffiti',
    'light',
    'neon',
    'orange',
    'overlay',
    'parchment',
    'red',
    'sand',
    'tan'
]

save_dir = 'chess_boards_all/'

for style in board_style:

    url = start_boards_url + style + mid_boards_url

    try:
        response = requests.get(url)
        response.raise_for_status()

        filename = os.path.join(save_dir, style + '.png')

        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f"Downloaded {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
