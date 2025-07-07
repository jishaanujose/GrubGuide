from groq import Groq
groq_api='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'
# Initialize the Groq client
client = Groq(api_key=groq_api,)

def speech_to_text(filename):
    with open(filename, "rb") as file:
            # Create a transcription of the audio file
        transcription = client.audio.transcriptions.create(
              file=file, # Required audio file
              model="whisper-large-v3-turbo", # Required model to use for transcription
              prompt="Specify context or spelling",  # Optional
              response_format="verbose_json",  # Optional
              timestamp_granularities = ["word", "segment"], # Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
              language="en",  # Optional
              temperature=0.0  # Optional
            )
    return transcription.text