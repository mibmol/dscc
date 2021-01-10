import requests
from config.utils import get_env

def submit_image(image_file):
    if image_file != None:
        url = 'https://api.imgur.com/3/image'
        payload = {'image': image_file.read()}
        headers = {
            'Authorization': 'Client-ID ' + get_env('IMGURL_CLIENT_ID')
        }

        res = requests.post(url, headers=headers, data=payload)
        return res.json()['data']['link']
    return None