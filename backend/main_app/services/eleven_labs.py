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

def convert_text_to_speech(user, message):
  headers = {
    "Accept": "application/json",
    "xi-api-key": settings.ELEVEN_LABS_API_KEY
  }
  endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{user.voice_config.voice_id}/stream"

  data = {
    "text": message,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
    "stability": user.voice_config.stability,
    "similarity_boost": user.voice_config.similarity_boost,
    "style": user.voice_config.style,
    "use_speaker_boost": user.voice_config.use_speaker_boost
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
  
def get_all_voices():
    headers = {
        "xi-api-key": settings.ELEVEN_LABS_API_KEY
    }

    response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers)
    if response.status_code == 200:
        return response.json().get("voices", [])
    else:
        return []
    
def filter_voices(accent=None, gender=None, age=None, description=None, use_case=None):
    all_voices = get_all_voices()

    filtered_voices = []
    for voice in all_voices:
        labels = voice.get("labels", {})
        if (
            (not accent or labels.get("accent", "").lower() == accent.lower()) and
            (not gender or labels.get("gender", "").lower() == gender.lower()) and
            (not age or labels.get("age", "").lower() == age.lower()) and
            (not description or labels.get("description", "").lower() == description.lower()) and
            (not use_case or labels.get("use_case", "").lower() == use_case.lower())
        ):
            filtered_voices.append({
                "voice_id": voice["voice_id"],
                "name": voice["name"],
                "preview_url": voice.get("preview_url"),
                "accent": labels.get("accent"),
                "gender": labels.get("gender"),
                "age": labels.get("age"),
                "description": labels.get("description"),
                "use_case": labels.get("use_case"),
            })

    return filtered_voices


def get_voice_settings(voice_id):
  headers = {
    "xi-api-key": settings.ELEVEN_LABS_API_KEY
  }
  response = requests.get(f"https://api.elevenlabs.io/v1/voices/{voice_id}/settings", headers=headers)

  if response.status_code == 200:
      return response.json()
  else:
    return {"error": "Failed to get voice settings", "status_code": response.status_code}


def update_voice_settings(voice_id, stability, similarity_boost, style, use_speaker_boost):
    headers = {
        "xi-api-key": settings.ELEVEN_LABS_API_KEY,
        "Content-Type": "application/json"
    }
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}/settings/edit"

    payload = {
        "stability": stability,
        "similarity_boost": similarity_boost,
        "style": style,
        "use_speaker_boost": use_speaker_boost
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to update voice settings", "status_code": response.status_code}