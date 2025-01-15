import json
from openai import OpenAI
from django.conf import settings

from ..models import MainTask, Subtask

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
    
def create_assistant(name="Unknown"):
    """
    You currently cannot set the temperature for Assistant via the API.
    """
    assistant = client.beta.assistants.create(
        name=f"{name}'s Todo app Assistant",
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
                        "main_task": {
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
                    "required": ["main_task", "subtasks"]
                }
            }
        }
    ]
    )
    return assistant # Save afterwards

def handle_function_calling(run, user):
    """
    Handles the required actions from the assistant.
    """
    tool_outputs = []

    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        # IF add_task WAS CALLED BY AI
        if tool_call.function.name == "add_task":
            # Save task to MainTask
            arguments = json.loads(tool_call.function.arguments)
            task_title = arguments["task"]

            MainTask.objects.create(
                user=user,
                title=task_title,
            )

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({"status": "success", "task": task_title})
            })
        # IF add_decomposed_task WAS CALLED BY AI
        elif tool_call.function.name == "add_decomposed_task":
            # Save decomposed tasks
            arguments = json.loads(tool_call.function.arguments)
            main_task_title = arguments["main_task"]
            subtasks = arguments["subtasks"]

            main_task = MainTask.objects.create(
                user=user,
                title=main_task_title,
            )

            for subtask_title in subtasks:
                Subtask.objects.create(
                    main_task=main_task,
                    title=subtask_title,
                )

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({
                    "status": "success",
                    "main_task": main_task_title,
                    "subtasks": subtasks,
                })
            })

    if tool_outputs:
        submit_tool_outputs(run.thread_id, run.id, tool_outputs)

def create_thread():
    return client.beta.threads.create() # Save afterwards

def add_message_to_thread(thread_id, message_body):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )
    return message

def run_assistant(thread_id, assistant_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    return run

def retrieve_current_run(thread_id, run_id):
    run = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    )
    return run

def retrieve_assistant_response(thread_id):
    message = client.beta.threads.messages.list(thread_id=thread_id)
    return message

def submit_tool_outputs(thread_id, run_id, tool_outputs):
    run = client.beta.threads.runs.submit_tool_outputs_and_poll(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs,
    )
    return run
    
def cancel_active_run(thread_id):
        """
        Cancels the active run for the given thread_id.
        """
        try:
            # Get active runs for the thread
            active_runs = client.beta.threads.runs.list(thread_id=thread_id)
            for run in active_runs.data:
                if run.status != "completed":
                    # Cancel the active run
                    client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run.id)
                    print(f"Cancelled active run: {run.id}")
        except Exception as e:
            print(f"Error while canceling active run: {e}")