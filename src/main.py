import dotenv
import os

# Setting section
dotenv.load_dotenv(".env")
YOUTUBE_API_KET: str = os.getenv("YOUTUBE_API_KEY")
GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
if YOUTUBE_API_KET is None or GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise ValueError("One or more environment variables are not set.")

def main() -> None:

    return

if __name__ == "__main__":
    main()