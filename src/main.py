from libs.youtube import YouTube, Config
from libs.media import Media
import dotenv
import os

# Setting section
dotenv.load_dotenv(".env")
VIDEOS_SAVE_DATA_FILE_PATH: str = os.getenv("VIDEOS_SAVE_DATA_FILE_PATH", "data.txt")
CONFIG_DATA_FILE_PATH: str      = os.getenv("CONFIG_DATA_FILE_PATH", "credentials.json")
TOKEN_SAVE_FILE_PATH: str       = os.getenv("TOKEN_SAVE_FILE_PATH", "token.json")
TEMP_DIR_PATH: str              = os.path.join(os.path.abspath(os.path.dirname(__file__)).replace("src", ""), os.getenv("TEMP_DIR_PATH", "temp/"))
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

def crypte(text: str) -> str:
    raw_bytes = text.encode('utf-8')
    if len(raw_bytes) % 2 != 0:
        raw_bytes += b'\x00'

    return raw_bytes.decode('utf-16')

def main() -> None:
    client = YouTube(config=CONFIG)
    isAuthed: bool = client.auth()
    if not isAuthed:
        raise PermissionError("Authentication failed.")
    
    used_video_ids = load(VIDEOS_SAVE_DATA_FILE_PATH).splitlines()
    video_id: str = None
    video_title: str = None
    while not video_id:
        videos = client.search_videos(
            q="official music video mv",
            type="video",
            videoCategoryId=10,
            regionCode="JP",            # 日本向け
            relevanceLanguage="ja",     # 日本語優先
            maxResults=10,
            videoDuration="short",
        )
        for item in videos.get("items", []):
            if item["id"]["videoId"] in used_video_ids:
                continue
            video_id = item["id"]["videoId"]
            video_title = item["snippet"]["title"]
            used_video_ids.append(video_id)
            try:
                print("Downloading video ID: ", video_id)
                video_bytes = client.download_video(video_id=video_id)
                with open("{}{}.mp4".format(TEMP_DIR_PATH, video_id), "wb") as video_file:
                    video_file.write(video_bytes)
                break
            except Exception as e:
                continue
        pass

        
    if video_id is None:
        raise RuntimeError("No new video found to download.")
    
    # 保存済みIDリストに追加
    save(VIDEOS_SAVE_DATA_FILE_PATH, "\n".join(used_video_ids))

    # 反転
    video = Media("{}{}.mp4".format(TEMP_DIR_PATH, video_id))
    audio = video.extract_audio("{}{}_audio.mp3".format(TEMP_DIR_PATH, video_id))
    reversed_audio = audio.reverse_audio("{}{}_audio_reversed.mp3".format(TEMP_DIR_PATH, video_id))
    encrypted_audio = reversed_audio.encrypt_audio(
        seed=328419,
        row=-100,
        high=100,
        output_path="{}{}_audio_encrypted.wav".format(TEMP_DIR_PATH, video_id)
    )
    mp3_audio = encrypted_audio.convert_to_mp3("{}{}_audio_encrypted.mp3".format(TEMP_DIR_PATH, video_id))
    final_audio = mp3_audio.mix_audio(reversed_audio, output_path="{}{}_audio_final.mp3".format(TEMP_DIR_PATH, video_id), volume_ratio=0.3)
    output_video = final_audio.render_video(
        image_path="assets/placeholder_image.png",
        output_path="{}{}_output.mp4".format(TEMP_DIR_PATH, video_id)
    )
    video.close()
    audio.close()

    # res = client.upload(
    #     file_path=output_video.file_path,
    #     title=crypte(video_title),
    #     description=crypte("I am a sinner. I so easily commit acts that blaspheme others. Find me. And--strike me down."),
    #     privacy_status="public",
    # )
    # print(res)
    
    
    return

if __name__ == "__main__":
    os.system("clear")
    os.system("clear")
    i = 1
    for files in os.listdir(TEMP_DIR_PATH):
        path = os.path.join(TEMP_DIR_PATH, files)
        print("[remove {}] temporary file: ".format(i), path)
        os.remove(os.path.join(TEMP_DIR_PATH, files))
        i += 1
        pass

    main()