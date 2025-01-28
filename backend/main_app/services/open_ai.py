import io
import json
import os
import subprocess
import tempfile
from openai import OpenAI
from django.conf import settings

from ..models import MainTask, Subtask

client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
def fetch_openai_response(context):
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
        with open("test.wav", "wb") as buffer:
            buffer.write(audio_file.file.read())

        audio_input = open("test.wav", "rb")

        response = client.audio.transcriptions.create(
            file=audio_input,
            model="whisper-1"
        )

        os.remove("test.wav")
        return response.text
    except subprocess.CalledProcessError as e:
        return f"Error during file conversion: {e.stderr.decode()}"
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
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the task"
                    },
                    "due_date": {
                        "type": "string",
                        "description": "Date until the task should be done"
                    },
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
        },
        {
            "type": "function",
            "function": {
                "name": "get_tasks",
                "description": "Fetch main tasks and their subtasks from the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "include_completed": {
                            "type": "boolean",
                            "description": "Whether to include completed tasks"
                        }
                    },
                    "required": ["include_completed"]
                }
            }
        },
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
            task_description = arguments["description"] if "description" in arguments else None
            task_due_date = arguments["due_date"] if "due_date" in arguments else None

            task_data = MainTask.objects.create(
                user=user,
                title=task_title,
                description=task_description,
                due_date=task_due_date
            )

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({"status": "success", "task": task_data})
            })
        # IF add_decomposed_task WAS CALLED BY AI
        elif tool_call.function.name == "add_decomposed_task":
            # Save decomposed tasks
            arguments = json.loads(tool_call.function.arguments)
            main_task_title = arguments["main_task"]
            subtasks_titles = arguments["subtasks"]
            subtasks = []

            main_task = MainTask.objects.create(
                user=user,
                title=main_task_title,
            )

            for subtask_title in subtasks_titles:
                subtasks.append(Subtask.objects.create(
                    main_task=main_task,
                    title=subtask_title,
                ))

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({
                    "status": "success",
                    "main_task": main_task,
                    "subtasks": subtasks,
                })
            })

        # IF get_tasks WAS CALLED BY AI
        elif tool_call.function.name == "get_tasks":
            arguments = json.loads(tool_call.function.arguments)
            include_completed = arguments["include_completed"]
            if include_completed:
                tasks = MainTask.objects.filter(user=user).prefetch_related("subtasks").order_by("-created_at")
            else:
                tasks = MainTask.objects.filter(user=user, is_completed=False).prefetch_related("subtasks").order_by("-created_at")
            tasks_data = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "created_at": task.created_at.isoformat(),
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "is_completed": task.is_completed,
                    "subtasks": [
                        {
                            "id": subtask.id,
                            "title": subtask.title,
                            "due_date": subtask.due_date.isoformat() if subtask.due_date else None,
                            "is_completed": subtask.is_completed,
                        }
                        for subtask in task.subtasks.all()
                    ],
                }
                for task in tasks
            ]

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({"status": "success", "tasks": tasks_data}),
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