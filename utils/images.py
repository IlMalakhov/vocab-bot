import requests
import os
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY")

def fetch_image_url(word):
    url = f"https://api.unsplash.com/search/photos"
    params = {
        "query": word,
        "client_id": UNSPLASH_API_KEY,
        "per_page": 1  # top result
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]["urls"]["small"]
        return None
    else:
        print(f"images.py: Unable to fetch image for {word}")
        return None