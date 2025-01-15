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
    
def create_assistant():
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name="Todo app Assistant",
        instructions=(
            "You're a helpful assistant in the todo app that can assist users to add tasks to the todo list. "
            "Be friendly and funny. If the task is complex, suggest decomposing it into subtasks and provide options. "
            "Ask the user if they agree with the subtasks or want to modify them. "
            "If the user confirms, use the function to add the subtasks. If the user provides changes, update the subtasks accordingly before adding them."
        ),
        model="gpt-4o",
        tools=[
        {
            "type": "function",
            "function": {
            "name": "add_task",
            "description": "Add task to db",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task a user asked to add"
                    }
                },
                "required": ["task"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_decomposed_task",
                "description": "Add decomposed tasks to the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "parent_task": {
                            "type": "string",
                            "description": "The original task that was decomposed"
                        },
                        "subtasks": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "List of decomposed subtasks"
                        }
                    },
                    "required": ["parent_task", "subtasks"]
                }
            }
        }
    ]
    )
    return assistant # Save afterwards

def create_thread():
    return client.beta.threads.create() # Save afterwards

def add_message_to_thread(thread_id, message_body):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )
    return message