import requests
import yaml
import os

# Load the config file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '../config/config.yaml')
with open(CONFIG_FILE, 'r') as file:
    config = yaml.safe_load(file)

# Twitch API URLs and credentials
TWITCH_CLIENT_ID = config['twitch']['client_id']
TWITCH_CLIENT_SECRET = config['twitch']['client_secret']
CATEGORIES = config['twitch']['categories']
BASE_URL = "https://api.twitch.tv/helix"

# Function to authenticate and get OAuth token
def get_twitch_oauth_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.json()["access_token"]

# Function to get the top clips for a given game/category name
def get_top_clips(category_name, oauth_token, limit=5):
    headers = {
        "Client-ID": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {oauth_token}"
    }

    # Step 1: Get the game/category ID based on its name
    game_search_url = f"{BASE_URL}/games"
    params = {"name": category_name}
    game_response = requests.get(game_search_url, headers=headers, params=params)
    game_response.raise_for_status()
    
    if not game_response.json()["data"]:
        print(f"Category '{category_name}' not found.")
        return []

    game_id = game_response.json()["data"][0]["id"]

    # Step 2: Get the top clips for this game/category
    clips_url = f"{BASE_URL}/clips"
    params = {
        "game_id": game_id,
        "first": limit,
        "sort": "views",  # You can use other sort options like "trending" or "time"
    }
    clips_response = requests.get(clips_url, headers=headers, params=params)
    clips_response.raise_for_status()
    return clips_response.json()["data"]

# Main script to fetch clips for all specified categories
if __name__ == "__main__":
    # Step 1: Get OAuth token
    oauth_token = get_twitch_oauth_token()
    
    # Step 2: Iterate over each category in config and get top clips
    all_clips = {}
    for category in CATEGORIES:
        print(f"Fetching top clips for category: {category}")
        clips = get_top_clips(category, oauth_token)
        all_clips[category] = clips
        print(f"Retrieved {len(clips)} clips for category '{category}'.")

    # Step 3: Save results to a local file (JSON format)
    import json
    with open("top_clips.json", "w") as f:
        json.dump(all_clips, f, indent=4)
    print("Top clips saved to 'top_clips.json'.")
