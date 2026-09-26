import io
import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key)

# Your copied voice ID
VOICE_ID = "Vs5CmVCVJwW4odQS2pVf"

def speak(text: str):
    print(f"Generating audio for: '{text}'")
    try:
        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128",
        )

        audio_bytes = b"".join(audio_stream)
        print(f"Success! Received {len(audio_bytes)} bytes of audio.")

        # Save to a quick mp3 file to test playback
        with open("output.mp3", "wb") as f:
            f.write(audio_bytes)
        
        # Play using Windows default media player
        os.system("start output.mp3")

    except Exception as e:
        print(f"Error caught: {e}")

if __name__ == "__main__":
    speak("Hello! The ElevenLabs audio system is fully operational.")