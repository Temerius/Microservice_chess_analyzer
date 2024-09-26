import os
import requests

start_figures_url = "https://images.chesscomfiles.com/chess-themes/pieces/"
mid_figures_url = "/150/"
figure_style = [
    'neo',
    'game_room',
    'wood',
    'glass',
    'gothic',
    'classic',
    'metal',
    'bases',
    'neo_wood',
    'icy_sea',
    'club',
    'ocean',
    'newspaper',
    'blindfold',
    'space',
    'cases',
    'condal',
    '3d_chesskid',
    '8_bit',
    'marble',
    'book',
    'alpha',
    'bubblegum',
    'dash',
    'graffiti',
    'light',
    'lolz',
    'luca',
    'maya',
    'modern',
    'nature',
    'neon',
    'sky',
    'tigers',
    'tournament',
    'vintage',
    '3d_staunton',
    '3d_wood',
    '3d_plastic'
]
png_figures_list = [
    'br.png',
    'bn.png',
    'bb.png',
    'bq.png',
    'bk.png',
    'bp.png',
    'wr.png',
    'wn.png',
    'wb.png',
    'wq.png',
    'wk.png',
    'wp.png'
]

for style in figure_style:

    url = start_figures_url + style + mid_figures_url

    image_urls = [url + i for i in png_figures_list]

    save_dir = './images/chess_pieces_all/' + f'{style}'
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
