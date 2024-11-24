import requests

from django.conf import settings

VOICE_ALICE = "Xb7hH8MSUJpSbSDYk0k2"

# Aria; 9BWtsMINqrJLrRacOk9x
# Roger; CwhRBWXzGAHq8TQ4Fs17
# Sarah; EXAVITQu4vr4xnSDxMaL
# Laura; FGY2WhTYpPnrIDTdsKH5
# Charlie; IKne3meq5aSn9XLyUdCD
# George; JBFqnCBsd6RMkjVDRZzb
# Callum; N2lVS1w4EtoT3dr4eOWO
# River; SAz9YHcvj6GT2YYXdXww
# Liam; TX3LPaxmHKxFdv7VOQHJ
# Charlotte; XB0fDUnXU5powFXDhCwa
# Alice; Xb7hH8MSUJpSbSDYk0k2
# Matilda; XrExE9yKIg1WjnnlVkGX
# Will; bIHbv24MWmeRgasZH58o
# Jessica; cgSgspJ2msm6clMCkdW9
# Eric; cjVigY5qzO86Huf0OWal
# Chris; iP95p4xoKVk53GoZ742B
# Brian; nPczCjzI2devNBz1zQrb
# Daniel; onwK4e9ZLuTAKqWW03F9
# Lily; pFZP5JQG7iQjIQuC4Bku
# Bill; pqHfZKP75CvOlQylNhV4

def convert_text_to_speech(message):
  headers = {
    "Accept": "application/json",
    "xi-api-key": settings.ELEVEN_LABS_API_KEY
  }
  endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ALICE}/stream"

  data = {
    "text": message,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.8,
    "style": 0.0,
    "use_speaker_boost": True
    }
  }

  try:
    response = requests.post(endpoint, headers=headers, json=data, stream=True)
  except Exception as e:
     return f"Error while fetching response from ElevenLabs: {str(e)}"
  
  if response.status_code == 200:
    return response.content
  else:
    return