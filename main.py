import random
import string
import time
import requests
import urllib.parse

from configuration import VK, LastFM


def get_json(url):
    output = requests.get(url).json()
    return output


def char_trim(string, limit):
    # Trim string if it has more than N chars (and add '…' to the end)
    if len(string) > limit:
        return string[:limit] + "…"
    else:
        return string

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def set_vk(about):
    get_json(
        f"https://api.vk.com/method/status.set?text={urllib.parse.quote_plus(about) + ' [' +id_generator(4) + ']'}&access_token={VK.token}&v=5.81")


def get_current_playing():
    limit = 60
    json = get_json(
        f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&api_key={LastFM.api_key}&user={LastFM.username}&limit=1&format=json")
    current_track = json["recenttracks"]["track"][0]

    artist = "Unknown Artist"
    track = "Unknown Track"

    common_name = None

    if ("@attr" in current_track) and ("nowplaying" in current_track["@attr"]) and (
            current_track["@attr"]["nowplaying"] == "true"):
        # Artist name
        if ("artist" in current_track) and ("#text" in current_track["artist"]) and (current_track["artist"]["#text"]):
            artist = char_trim(string=current_track["artist"]["#text"], limit=limit)

        # Track name
        if ("name" in current_track) and (current_track["name"]):
            # Checking if we can extend the limit (if Artist name string is less than {limit + 1})
            if ((limit + 1) - len(artist)) > 0:
                limit = limit + (limit - len(artist))
            track = char_trim(string=current_track["name"], limit=limit)

        common_name = "🎶 [" + track + "] — " + artist + " 🎶 on Spotify®"
    return common_name


last_track_name = None
audio_was_stopped = False
counter = 0

while True:
    counter += 1
    wait_time = random.randint(60 * 3, 60 * 5)

    currentTimeStamp = int(time.time())

    try:
        currentTrack = get_current_playing()
        if currentTrack:
            if (currentTrack != last_track_name) or audio_was_stopped:
                audio_was_stopped = False

                last_track_name = currentTrack
                print(f"[{counter}] <|Sleeping: {wait_time}|> {currentTrack}")
                set_vk(about=currentTrack)

        else:
            audio_was_stopped = True
            set_vk(about=VK.default_status)

    except Exception as e:
        print(f"[ERROR]: {e}")
    time.sleep(wait_time)
