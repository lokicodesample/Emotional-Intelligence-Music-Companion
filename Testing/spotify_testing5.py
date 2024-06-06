import requests
import pygame

url = 'https://api.spotify.com/v1/search'
params = {'q': 'happy', 'type': 'track','limit':'2'}
headers = {'Authorization': 'Bearer BQCEtiQ48uymiFNXS5Ak35RcZH5JnHPJ5xdFQ9-6D4wuXqqggIYAhYNqnreYoJIfMk4NHOsOPQFHZDpbBWn2isKFKYvDFQN8d1yjbgL0Y9McDbykl34'}

def play_music(url):
    response = requests.get(url)
    with open("audio.mp3","wb") as f:
         f.write(response.content)

    pygame.mixer.init()
    pygame.mixer.music.load("audio.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

try:
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    print(data)
    preview_url = data['tracks']['items'][0]['preview_url']
    play_music(preview_url)
except Exception as e:
    print("Error:", e)
