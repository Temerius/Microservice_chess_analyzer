import os
import requests

start_bg_url = "https://images.chesscomfiles.com/chess-themes/backgrounds/originals/large/"
mid_bg_url = ".png"
bg_style = [
    'game_room',
    'light',
    'wood',
    'glass',
    'tournament',
    'staunton',
    'newspaper',
    'tigers',
    'nature',
    'sky',
    'ocean',
    'metal',
    'gothic',
    'marble',
    'neon',
    'graffiti',
    'bubblegum',
    'lolz',
    'icy_sea',
]

save_dir = 'bg_all/'

for style in bg_style:

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
