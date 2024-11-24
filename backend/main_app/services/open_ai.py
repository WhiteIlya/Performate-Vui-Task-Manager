from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
def fetch_openai_response(context):
    # recent_context = _get_recent_context(user)
    # recent_context.append({"role": "user", "content": user_input})
    # system_message = {
    #     "role": "system",
    #     "content": (
    #         "Your task is to understand whether the task I ask you to help with is hard or not. "
    #         "Ask me if I want to decompose the task into smaller, easier tasks, and suggest decomposition variants."
    #     )
    # }
    # messages = [system_message] + recent_context
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=context
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error while fetching response from OpenAI: {str(e)}"
    

def convert_audio_to_text(audio_file):
    try:
        response = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1"
        )
        return response.text
    except Exception as e:
        return f"Error while fetching response from OpenAI: {str(e)}"