import dotenv
import os

# Setting section
dotenv.load_dotenv(".env")
YOUTUBE_API_KET: str = os.getenv("YOUTUBE_API_KEY")
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
if YOUTUBE_API_KET is None or GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise ValueError("One or more environment variables are not set.")

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
    used_video_ids = open("used_video_ids.txt", "r").read().splitlines()
    return

if __name__ == "__main__":
    main()