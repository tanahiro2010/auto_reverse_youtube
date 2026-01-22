from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os

class Config:
    apiKey:       str
    creditsPath:  str
    savedataPath: str
    scopes:       list[str]

    def __init__(self, apiKey: str, creditsPath: str, savedataPath: str, scopes: list[str]) -> None:
        self.apiKey       = apiKey
        self.creditsPath  = creditsPath
        self.savedataPath = savedataPath
        self.scopes       = scopes
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
    

