from libs.youtube import YouTube, Config

import dotenv
import os

# Setting section
dotenv.load_dotenv(".env")
VIDEOS_SAVE_DATA_FILE_PATH: str = os.getenv("VIDEOS_SAVE_DATA_FILE_PATH", "data.txt")
CONFIG_DATA_FILE_PATH: str      = os.getenv("CONFIG_DATA_FILE_PATH", "credentials.json")
TOKEN_SAVE_FILE_PATH: str       = os.getenv("TOKEN_SAVE_FILE_PATH", "token.json")
TEMP_DIR_PATH: str              = os.getenv("TEMP_DIR_PATH", "temp/")
if not CONFIG_DATA_FILE_PATH or not TOKEN_SAVE_FILE_PATH:
    raise ValueError("Configuration file path or token save file path is not set in environment variables.")

CONFIG = Config(
    creditsPath=CONFIG_DATA_FILE_PATH,
    savedataPath=TOKEN_SAVE_FILE_PATH,
    scopes=[
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.upload"
    ]
)

# utility functions
def load(file_path: str) -> str:
    try:
        with open(file_path, "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {file_path} was not found.")
    
    return

def save(file_path: str, content: str) -> None:
    try:
        with open(file_path, "w") as file:
            file.write(content)
        return
    except IOError as e:
        raise IOError(f"An error occurred while writing to {file_path}: {e}")
    
    return

def main() -> None:
    client = YouTube(config=CONFIG)
    isAuthed: bool = client.auth()
    if not isAuthed:
        raise PermissionError("Authentication failed.")
    
    used_video_ids = load(VIDEOS_SAVE_DATA_FILE_PATH).splitlines()
    video_id: str = None
    while not video_id:
        videos = client.search_videos(
            q="official music video mv",
            type="video",
            videoCategoryId=10,
            maxResults=10,
            videoDuration="short",
        )
        for item in videos.get("items", []):
            if item["id"]["videoId"] in used_video_ids:
                continue
            video_id = item["id"]["videoId"]
            try:
                video_bytes = client.download_video(video_id=video_id)
                with open("{}{}.mp4".format(TEMP_DIR_PATH, video_id), "wb") as video_file:
                    video_file.write(video_bytes)
                break
            except Exception as e:
                continue

            pass
        pass

        
    if video_id is None:
        raise RuntimeError("No new video found to download.")
    
    # 保存済みIDリストに追加
    used_video_ids.append(video_id)
    save(VIDEOS_SAVE_DATA_FILE_PATH, "\n".join(used_video_ids))

    # 反転

    

    
    return

if __name__ == "__main__":
    main()