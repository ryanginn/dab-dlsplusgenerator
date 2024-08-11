import requests
from datetime import datetime
import time

# URL of the Icecast server stream
url = "https://[ip]/status-json.xsl?mount=/radio2.mp3"

last_content = None

# Maximum number of retries
max_retries = 30000

def fetch_and_process_metadata():
    global last_content
    retries = 0

    while retries < max_retries:
        try:
            response = requests.get(url)
            response.raise_for_status() 
            data = response.json()
            title = data.get('icestats', {}).get('source', {}).get('title', '')
            prefix = "Now playing: "
            if " - " in title:
                artist, song_title = title.split(" - ", 1)
                current_content = f"Title: {song_title} - Artist: {artist}"
                artist_start_marker = len(prefix)  
                artist_length_marker = len(artist) - 1 
                song_start_marker = artist_start_marker + len(artist) + 3 
                song_length_marker = len(song_title) - 1  
                dls_plus_output = f"""##### parameters {{ #####
DL_PLUS=1
DL_PLUS_ITEM_TOGGLE=0
DL_PLUS_ITEM_RUNNING=1
# This tags "{artist}" as ITEM.ARTIST
DL_PLUS_TAG=4 {artist_start_marker} {artist_length_marker}
# This tags "{song_title}" as ITEM.TITLE
DL_PLUS_TAG=1 {song_start_marker} {song_length_marker}
##### parameters }} #####
{prefix}{title}""" 
                
                with open('/home/ryan/dab/mot/P02/INFO.dls', 'w') as file:
                    file.write(dls_plus_output)
            else:
                current_content = title
                with open('/home/ryan/dab/mot/P02/INFO.dls', 'w') as file:
                    file.write(title)
            if current_content != last_content:
                last_content = current_content
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"[{current_time}] - Content updated: {current_content}")
            else:
                print("No content update needed.")
            break

        except (requests.RequestException, ValueError) as e:
            print(f"Error: {e}. Retrying ({retries + 1}/{max_retries})...")
            retries += 1
            time.sleep(1)

    if retries == max_retries:
        print("Failed to fetch data after maximum retries. Stopping the program.")
while True:
    fetch_and_process_metadata()
    time.sleep(5)
