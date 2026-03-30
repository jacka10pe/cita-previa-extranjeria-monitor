import requests

photo_path = '/tmp/2026-03-14_16-03.png'

url = f"https://api.telegram.org/botXXX:YYY/sendPhoto"

# Open the image in binary mode
with open(photo_path, 'rb') as photo:
    payload = {
        'chat_id': ZZZ
    }
    files = {
        'photo': photo
    }
    response = requests.post(url, data=payload, files=files)

print(response.json())
