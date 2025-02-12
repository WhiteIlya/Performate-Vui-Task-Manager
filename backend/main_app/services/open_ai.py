from datetime import timedelta
import io
import json
import os
import subprocess
from openai import OpenAI
from django.conf import settings
from django.utils.timezone import now

from ..serializers import MainTaskSerializer

from ..models import MainTask, Subtask, Notification

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
            "You're a helpful assistant who follows persuasive system design principles in the todo app that can assist users to add tasks to the todo list. Dont answer too long but mostly it is up to you "
            "Be friendly and funny. If the task is complex, suggest decomposing it into subtasks and provide options. "
            "Ask the user if they agree with the subtasks or want to modify them. "
            "If the user confirms, use the function to add the subtasks. If the user provides changes, update the subtasks accordingly before adding them."
            # "After each query check due date tasks to fetch notifications and amount of times you have reminded but it is for you rather than for user to know."
            # "Remind the user and suggest taking action proactively according to the output of fetch notifications."
            "After each user request, check for upcoming tasks with deadlines check_due_date_tasks. You will receive a list of tasks along with the number of times you have already reminded the user."
            "Do not mention this count to the user."
            "It is only up to you to decide how often to remind the user. You know both the deadline of the task and the amount of times you have reminded the user."
            "Use create_notifications function to create notifications for the user if you decided to remind the user about a coming task to accomplish."
            "Follow PSD principles and do not overwhelm much user with the reminders but encourage the user to take action."
            "Make reminders engaging and persuasive, using humor, urgency, or motivational language."
            "If multiple tasks are due soon, prioritize the most urgent ones first."
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
            {
                "type": "function",
                "function": {
                    "name": "check_due_date_tasks",
                    "description": "Fetch tasks that are due soon for reminders"
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_notifications",
                    "description": "Create notifications for the user for selected tasks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_ids": {
                                "type": "array",
                                "items": {
                                    "type": "number"
                                },
                                "description": "List of task IDs for which notifications should be created."
                            },
                        },
                        "required": ["task_ids"]
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

            serialized_task = MainTaskSerializer(task_data).data

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({"status": "success", "task": serialized_task})
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

            serialized_main_task = MainTaskSerializer(main_task).data
            serialized_subtasks = [{"id": subtask.id, "title": subtask.title} for subtask in subtasks]

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({
                    "status": "success",
                    "main_task": serialized_main_task,
                    "subtasks": serialized_subtasks,
                })
            })

        # IF get_tasks WAS CALLED BY AI
        elif tool_call.function.name == "get_tasks":
            print("I was in the get_tasks function")
            arguments = json.loads(tool_call.function.arguments)
            include_completed = arguments["include_completed"]
            if include_completed:
                tasks = MainTask.objects.filter(user=user).prefetch_related("subtasks").order_by("-created_at")
            else:
                tasks = MainTask.objects.filter(user=user, is_completed=False).prefetch_related("subtasks").order_by("-created_at")

            tasks_data = MainTaskSerializer(tasks, many=True).data

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({"status": "success", "tasks": tasks_data}),
            })

        # IF check_due_date_tasks WAS CALLED BY AI
        elif tool_call.function.name == "check_due_date_tasks":
            print("I was in the check_due_date_tasks function")
            upcoming_tasks = MainTask.objects.filter(
                user=user,
                # due_date__gte=now(), # due_date >= now
                # due_date__lte=now() + timedelta(days=2), # due_date <= now + 1 day
                # # => due_date between now and now + 1 day
                is_completed=False
            )

            serialized_tasks = MainTaskSerializer(upcoming_tasks, many=True).data

            task_data = []
            for task in serialized_tasks:
                task_id = task["id"]
                task["you_have_reminded_count"] = Notification.objects.filter(main_task_id=task_id).count()
            
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({
                    "status": "success",
                    "tasks": serialized_tasks,
                })
            })
        
        # IF create_notifications WAS CALLED BY AI
        elif tool_call.function.name == "create_notifications":
            print("I was in the create notifications function")
            arguments = json.loads(tool_call.function.arguments)
            task_ids = arguments["task_ids"]

            notifications = []
            for task_id in task_ids:
                try:
                    task = MainTask.objects.get(id=task_id, user=user)
                    reminder_count = Notification.objects.filter(main_task=task).count()

                    Notification.objects.create(
                        user=user,
                        main_task=task,
                        reminder_count=reminder_count + 1
                    )

                    notifications.append({"task_id": task_id, "reminder_count": reminder_count + 1})
                except MainTask.DoesNotExist:
                    continue

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({
                    "status": "success",
                    "created_notifications": notifications,
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