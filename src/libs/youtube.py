from __future__ import annotations
from requests import Response
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests
import pickle
import os

class Config:
    creditsPath:  str
    savedataPath: str
    scopes:       list[str]
    base_url:     str

    def __init__(self, creditsPath: str, savedataPath: str, scopes: list[str], base_url: str = "https://ytdl-next.tanahiro2010.com") -> None:
        self.creditsPath  = creditsPath
        self.savedataPath = savedataPath
        self.scopes       = scopes
        self.base_url     = base_url
        return
    

class YouTube:
    config: Config
    client: any
    def __init__(self, config: Config) -> None:
        self.config = config
        return
    
    def auth(self) -> bool:
        creds = None
        scopes = self.config.scopes
        pickle_file = self.config.savedataPath

        if os.path.exists(pickle_file):
            with open(pickle_file, "rb") as token:
                creds = pickle.load(token)

        try:
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.creditsPath,
                    scopes=scopes
                )
                creds = flow.run_local_server(port=0)

                with open(pickle_file, "wb") as token:
                    pickle.dump(creds, token)

            self.client = build("youtube", "v3", credentials=creds)
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

        return True
    
    def get_videos(self, **kwargs) -> dict:
        request = self.client.videos().list(
            part="snippet,contentDetails,statistics",
            **kwargs
        )
        response = request.execute()
        return response
    
    def search_videos(self, **kwargs) -> dict:
        request = self.client.search().list(
            part="snippet",
            **kwargs
        )
        response = request.execute()
        return response
    
    def upload(self, file_path: str, title: str, description: str = "", tags: list[str] = None, category_id: str = "10", privacy_status: str = "private", made_for_kids: bool = False) -> dict:
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status,  # "public", "private", "unlisted"
                "madeForKids": made_for_kids
            }
        }
        
        media = MediaFileUpload(
            file_path,
            mimetype="video/*",
            resumable=True
        )
        
        request = self.client.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        response = request.execute()
        return response

    def download_video(self, video_id: str) -> bytes:
        endpoint = "{}/api".format(self.config.base_url)
        payload = {
            "url": "https://www.youtube.com/watch?v={}".format(video_id)
        }
        headers = {
            "User-Agent":           "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept":               "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5",
            "Accept-Language":      "ja,en-US;q=0.9,en;q=0.8",
            "Accept-Encoding":      "identity;q=1, *;q=0",
            "Range":                "bytes=0-",
            "Sec-Ch-Ua":            '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Sec-Ch-Ua-Mobile":     "?0",
            "Sec-Ch-Ua-Platform":   '"Windows"',
            "Sec-Fetch-Dest":       "video",
            "Sec-Fetch-Mode":       "no-cors",
            "Sec-Fetch-Site":       "cross-site"
        }
        session = requests.Session()
        session.headers.update(headers)


        response = requests.post(endpoint, json=payload)
        if not response.ok:
            raise ConnectionError("Failed to download video data from the external service.")
        
        data: dict = response.json()
        url: str | None = data.get("data", { "download_url": None }).get("download_url", None)
        response: Response = session.get(url)
        if not response.ok:
            raise ConnectionError("Failed to download video content from the provided URL.")
        
        return response.content