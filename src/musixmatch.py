import os
import requests
from logger import Logger
from song import Song
from bs4 import BeautifulSoup

MUSIXMATCH_API_KEY = os.getenv("MUSIXMATCH_API_KEY")


class MusixmatchApi:

    def __init__(self) -> None:
        self.client = None
        self.api_base_url = "https://api.musixmatch.com/ws/1.1/"
        self.logger = Logger("MusixmatchApi")

    def authenticate(self, api_key: str = MUSIXMATCH_API_KEY) -> bool:
        self.api_key = api_key
        self.logger.info("Successfully authenticated!")
        return True

    def _build_params(self, kwargs: dict = None) -> dict:
        kwargs["apikey"] = self.api_key
        return kwargs

    def get_song_id(self, song: Song) -> str:
        pass

    def get_song_url(self, song: Song) -> str:
        artists = " ".join(song.artists)
        search_query = f"{song.title} {artists}"
        params = {
            "q_track_artist": search_query,
            "s_track_rating": "desc"
        }
        response = requests.get(self.api_base_url + "track.search", params=self._build_params(params))
        if response.status_code != 200:
            self.logger.warning(f"Failed to get song url for song: {song}")
            return None
        if (status_code := response.json()["message"]["header"]["status_code"]) != 200:
            self.logger.warning(f"Got an HTTP code {status_code} from Musixmatch for song: {song}")
            return None
        track_url = response.json()["message"]["body"]["track_list"][0]["track"]["track_share_url"]
        track_url = track_url.split("?")[0]
        return track_url

    def get_lyrics_by_song_id(self, song_id: str) -> str:
        params = {
            "track_id": song_id,
        }
        response = requests.get(self.api_base_url + "track.lyrics.get", params=self._build_params(params))
        if response.status_code != 200:
            self.logger.warning(f"Failed to get lyrics for song_id: {song_id}")
            return None
        if (status_code := response.json()["message"]["header"]["status_code"]) != 200:
            self.logger.warning(f"Got an HTTP code {status_code} from Musixmatch for song_id: {song_id}")
            return None
        return response.json()["message"]["body"]["lyrics"]["lyrics_body"]


class MusixmatchScrapper:

    def __init__(self) -> None:
        self.logger = Logger("MusixmatchScrapper")
        self.base_url = "https://musixmatch.com/"

    def get_lyrics_by_song_url(self, song_url: str) -> str:
        lyrics = ""
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
        html_content = requests.get(song_url, headers=headers).content.decode('utf-8')

        soup = BeautifulSoup(html_content, 'html.parser')
        tags = soup.find_all("span", class_="lyrics__content__ok")
        for tag in tags:
            lyrics += tag.get_text().strip()
        return lyrics
