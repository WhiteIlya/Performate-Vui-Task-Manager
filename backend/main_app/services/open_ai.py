from datetime import timedelta
import pytz
import io
import json
import os
import subprocess
from openai import OpenAI
from django.conf import settings
from django.utils.timezone import now, localtime
from django.utils.dateparse import parse_datetime

from ..serializers import MainTaskSerializer, NotificationSerializer

from ..models import MainTask, Subtask, Notification

from .assistant_instructions import generate_instructions

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
    
def create_assistant(user):
    instructions = generate_instructions(user)

    assistant = client.beta.assistants.create(
        name=f"{user.full_name}'s Todo app Assistant called {user.voice_config.voice_name}",
        instructions=instructions,
    # "You're a helpful assistant who follows persuasive system design principles in the todo app that can assist users to add tasks to the todo list. Dont answer too long but mostly it is up to you "
    # "Ask the user if they agree with the subtasks or want to modify them. "
    # "If the user confirms, use the function to add the subtasks. If the user provides changes, update the subtasks accordingly before adding them."
    # "After each user request, check for upcoming tasks with deadlines check_due_date_tasks. You will receive a list of tasks along with the number of times you have already reminded the user."
    # "Do not mention this count to the user."
    # "It is only up to you to decide how often to remind the user. You know both the deadline of the task and the amount of times you have reminded the user."
    # "Use create_notifications function to create notifications for the user if you decided to remind the user about a coming task to accomplish."
    # "Follow PSD principles and do not overwhelm much user with the reminders but encourage the user to take action."
    # "Make reminders engaging and persuasive, using humor, urgency, or motivational language."
    # "If multiple tasks are due soon, prioritize the most urgent ones first."
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
                    "name": "get_current_date_time",
                    "description": "Fetch current time and date"
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
            {
                "type": "function",
                "function": {
                    "name": "update_user_ttm_stage",
                    "description": "Determine the user's behavior stage in the Transtheoretical Model (TTM). It is either Precontemplation, Contemplation, Preparation, Action, or Maintenance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ttm_stage": {
                                "type": "string",
                                "description": "New TTM stage for the user if he deserves to change it."
                            }
                        },
                        "required": ["ttm_stage"]
                    }
                }
            },
        ]
    )
    return assistant # Save afterwards

def modify_assistant_instruction(user):
    assistant_id = user.assistant_id
    instructions = generate_instructions(user)
    assistant = client.beta.assistants.update(
        assistant_id,
        instructions=instructions
    )

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

            if task_due_date:
                user_timezone = pytz.timezone(user.time_zone if user.time_zone else "Europe/Berlin")
                localized_due_date = user_timezone.localize(parse_datetime(task_due_date)).astimezone(pytz.UTC)
            else:
                localized_due_date = None

            task_data = MainTask.objects.create(
                user=user,
                title=task_title,
                description=task_description,
                due_date=localized_due_date
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

            user_timezone = pytz.timezone(user.time_zone if user.time_zone else "Europe/Berlin")

            upcoming_tasks = MainTask.objects.filter(
                user=user,
                # due_date__gte=now(), # due_date >= now
                # due_date__lte=now() + timedelta(days=2), # due_date <= now + 1 day
                # # => due_date between now and now + 1 day
                is_completed=False
            )

            serialized_tasks = MainTaskSerializer(upcoming_tasks, many=True).data

            for task in serialized_tasks:
                task_id = task["id"]
                task["you_have_reminded_count"] = Notification.objects.filter(main_task_id=task_id).count()
                task["notifications"] = NotificationSerializer(Notification.objects.filter(main_task_id=task_id), many=True).data
                
                if task["due_date"]:
                    due_date_dt = parse_datetime(task["due_date"])
                    
                    if due_date_dt and due_date_dt.tzinfo is None:
                        due_date_dt = due_date_dt.replace(tzinfo=pytz.UTC)
                    
                    task["due_date"] = localtime(due_date_dt, user_timezone).strftime("%Y-%m-%d %H:%M:%S %Z")
            
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

        # IF update_user_ttm_stage WAS CALLED BY AI
        elif tool_call.function.name == "update_user_ttm_stage":
            print("I was in the update_user_ttm_stage function")
            arguments = json.loads(tool_call.function.arguments)
            ttm_stage = arguments["ttm_stage"]

            user.voice_config.ttm_stage = ttm_stage
            user.voice_config.save()

            modify_assistant_instruction(user)

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({"status": "success", "current_user_ttm_stage": ttm_stage}),
            })

        elif tool_call.function.name == "get_current_date_time":
            print("I was in the get_current_date_time function")

            user_timezone = pytz.timezone(user.time_zone if user.time_zone else "Europe/Berlin")
            date_time = localtime(now(), user_timezone).strftime("%Y-%m-%d %H:%M:%S %Z")

            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "output": json.dumps({"status": "success", "date_time": date_time}),
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