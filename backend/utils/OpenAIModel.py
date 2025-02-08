from typing import Optional
import openai
import os
from dotenv import load_dotenv

class OpenAIModel:
    def __init__(self, 
                 embedding_model: str = "text-embedding-3-large", 
                 transcription_model: str = "whisper-1"):
        # Load environment variables from .env
        load_dotenv()
        self.embedding_model = embedding_model
        self.transcription_model = transcription_model
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key

    def create_embedding(self, text: str):
        """
        Create an embedding for the given text using the specified embedding model.
        :param text: The text to embed.
        :return: A list of floating point numbers representing the embedding.
        """
        response = openai.Embedding.create(
            input=text,
            model=self.embedding_model
        )
        # Extract the embedding vector from the response
        embedding = response["data"][0]["embedding"]
        return embedding

    def transcribe_audio(self, audio_path: str):
        """
        Transcribe speech from an audio file using OpenAI's Whisper model.
        :param audio_path: The file path to the audio file.
        :return: The transcribed text.
        """
        with open(audio_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe(self.transcription_model, audio_file)
        # Assuming the transcript is returned as a dictionary with a "text" key
        return transcript["text"]

    def join_content(self, speech_text: str, user_text: str, image_text: str, video_text: Optional[str] = None) -> str:
        """
        Join the content of the provided texts, ignoring any empty texts.
        """
        texts = [speech_text, user_text, image_text, video_text]
        non_empty_texts = [text for text in texts if text]
        return " ".join(non_empty_texts)

# Example usage:
if __name__ == "__main__":
    model = OpenAIModel()
    
    # Example: Generate an embedding
    text = "Hello world, this is a test."
    embedding = model.create_embedding(text)
    print("Embedding:", embedding)
    
    # Example: Transcribe an audio file (ensure the path is valid)
    # audio_path = "path_to_audio_file.wav"
    # transcription = model.transcribe_audio(audio_path)
    # print("Transcription:", transcription)

    # # Example: Join content
    # speech_text = "This is speech text."
    # user_text = "This is user text."
    # image_text = ""
    # video_text = "This is video text."
    # joined_text = model.join_content(speech_text, user_text, image_text, video_text)
    # print("Joined Text:", joined_text)