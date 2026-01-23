from moviepy import VideoFileClip
from pydub import AudioSegment

class Media:
    file_path: str
    clip: VideoFileClip
    dub: AudioSegment
    
    def __init__(self, file_path):
        file_format = file_path.split('.')[-1]
        if file_format not in ['mp4', 'mp3', 'wav', 'avi', 'mov']:
            raise ValueError(f"Unsupported media format: {file_format}")
        
        self.file_path = file_path
        if file_format in ['mp4', 'avi', 'mov']:
            self.clip = VideoFileClip(file_path)
            pass
        else:
            self.dub = AudioSegment.from_file(file_path, format=file_format)
            pass

        return
    

    def get_duration(self):
        return self.clip.duration

    def get_fps(self):
        return self.clip.fps

    def get_resolution(self):
        return self.clip.size
    
    def extract_audio(self, output_path) -> Media:
        audio = self.clip.audio
        audio.write_audiofile(output_path)
        return Media(output_path)
    
    def reverse(self, output_path) -> Media:
        reversed_clip = self.dub.reverse()
        reversed_clip.export(output_path, format="mp3")
        return Media(output_path)
    

    def close(self):
        self.clip.close()