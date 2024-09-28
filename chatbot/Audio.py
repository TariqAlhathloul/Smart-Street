import subprocess
import numpy as np
import sounddevice as sd
import wavio as wv
import os
import arabic_reshaper
from openai import OpenAI


from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

class Audio:

    def __init__(self):
        #sampling rate
        self.samplerate = 44100
        #duration of the recording in seconds
        self.senconds = 7
        self.frames = self.samplerate * self.senconds
        print("Chatbot initialized.")

    def record_audio(self)-> tuple:
        """"
        no parameters\n
        record audio, return the 'recording' and the 'sampling rate'
        """        
        #start recording the audio
        print("Listening...")
        recording = sd.rec(int(self.frames), samplerate=self.samplerate, channels=2, dtype='int16')
        sd.wait()
        print("Finished recording.")
        return recording, self.samplerate
    
    def write_audio(self, recording: np.ndarray, path:str) -> None:
        """
        the function will save the recording to a mp3 file\n
        recording: the audio recording\n
        return: None
        """
        # write audio to the file
        wv.write(path, recording, self.samplerate, sampwidth=2)

    def voice_to_text(self, audio_file_path: str) -> str:
        """
        audio_file_path: the path to the audio file\n
        return: string of the transcription
        """
        #assert the audio file is a mp3 or wav file
        assert audio_file_path.endswith(".mp3") or audio_file_path.endswith(".wav"), "the file should be a mp3 or wav file"
        #assert path exists
        assert os.path.exists(audio_file_path), "the path doesn't exist"
        with open(audio_file_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(model="whisper-1", file=audio_file)

        return transcription.text
    
    def text_to_voice(self, text: str, audio_file_path:str) -> None:
        """
        text: the text to convert to speech
        audio_file_path: the path to save the audio file
        """
        response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text
        )

        response.stream_to_file(audio_file_path)

    def play_sound(self, file_path: str) -> None:
        """
        file_path: the path to the audio file to play
        """
        try:
            subprocess.run(['ffplay', '-nodisp', '-autoexit', file_path])
        except FileNotFoundError:
            print("Error: ffplay is not installed or not in your PATH.")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def printAr(self, text: str) -> None:
        """
        reshapes the arabic text and print it\n
        text: the text to print
        """
        text = arabic_reshaper.reshape(text)
        print(text[::-1])