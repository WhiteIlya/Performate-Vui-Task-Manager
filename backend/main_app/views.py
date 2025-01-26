import base64
import time
import os
import tempfile
# from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.uploadedfile import UploadedFile
# from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .models import MainTask, Subtask

from .serializers import AssistantRequestSerializer, MainTaskSerializer
from .services.open_ai import (
    add_message_to_thread, 
    cancel_active_run, 
    create_assistant, 
    create_thread, 
    handle_function_calling, 
    retrieve_assistant_response, 
    retrieve_current_run, 
    run_assistant,
    convert_audio_to_text
)
from .services.eleven_labs import convert_text_to_speech


class AssistantAPIView(APIView):
    permission_classes = [IsAuthenticated]
    # parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = AssistantRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]

        user = request.user

        # Check if user has assistant_id and thread_id
        if not user.assistant_id or not user.thread_id:
            assistant = create_assistant(name=user.full_name)
            thread = create_thread()

            user.assistant_id = assistant.id
            user.thread_id = thread.id
            user.save()

        # Process the assistant interaction
        response_message = process_request_message_to_assistant(user, message)

        return Response({"response": response_message}, status=status.HTTP_200_OK)

        
    
class AudioToChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        audio_file: UploadedFile = request.FILES.get('file')
        if not audio_file:
            return Response({"error": "No audio file provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            text_message = convert_audio_to_text(audio_file)
        except Exception as e:
            return Response({"error": f"Failed to process audio: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            user = request.user
            response_message = process_request_message_to_assistant(user, text_message)
        except Exception as e:
            return Response({"error": f"Failed to process assistant message: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            audio_response = convert_text_to_speech(response_message)
            if not audio_response:
                raise ValueError("Failed to generate audio response")
            
            audio_base64 = base64.b64encode(audio_response).decode('utf-8')
        except Exception as e:
            return Response({"error": f"Failed to generate audio response: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"response": response_message, "input_text": text_message, "audio_response": audio_base64}, status=status.HTTP_200_OK)
    


def process_request_message_to_assistant(user, message):
        """
        Sends a message to the assistant and processes its response.
        """
        try:
            # Add the user's message to the thread
            add_message_to_thread(user.thread_id, message)
            # Run the assistant
            run = run_assistant(user.thread_id, user.assistant_id)

            # Handle the run and retrieve a response
            while run.status != "completed":
                if run.status == "requires_action":
                    handle_function_calling(run, user)
                time.sleep(0.5)
                run = retrieve_current_run(user.thread_id, run.id)  # To get the latest run update to check whether it's status has changed

            # Retrieve the assistant's response
            messages = retrieve_assistant_response(user.thread_id)
            return messages.data[0].content[0].text.value
        except Exception as e:
            # Handle active run error
            error_message = str(e)
            if "active" in error_message.lower():
                cancel_active_run(user.thread_id)
            raise e

class UserTasksAPIView(ListAPIView):
    """
    API view to fetch tasks for the authenticated user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = MainTaskSerializer

    def get_queryset(self):
        return MainTask.objects.filter(user=self.request.user).order_by('-created_at')


class UpdateTaskAPIView(APIView):
    """
    API view to update or edit a MainTask or SubTask.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        task_id = request.data.get("task_id")
        task_type = request.data.get("task_type")
        title = request.data.get("title")
        description = request.data.get("description")
        due_date = request.data.get("due_date")
        is_completed = request.data.get("is_completed")

        try:
            # Update MainTask
            if task_type == "main_task":
                task = MainTask.objects.get(id=task_id, user=request.user)
                if title is not None:
                    task.title = title
                if description is not None:
                    task.description = description
                if due_date is not None:
                    task.due_date = due_date
                if is_completed is not None:
                    task.is_completed = is_completed
                    if is_completed:
                        # Mark all subtasks as completed
                        task.subtasks.update(is_completed=True)
                task.save()

            # Update SubTask
            elif task_type == "subtask":
                subtask = Subtask.objects.get(id=task_id, main_task__user=request.user)
                if title is not None:
                    subtask.title = title
                if is_completed is not None:
                    subtask.is_completed = is_completed
                subtask.save()

                # If all subtasks are completed, mark MainTask as completed
                # main_task = subtask.main_task
                # if not main_task.subtasks.filter(is_completed=False).exists():
                #     main_task.is_completed = True
                #     main_task.save()

            else:
                return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": "Task updated successfully"}, status=status.HTTP_200_OK)

        except MainTask.DoesNotExist:
            return Response({"error": "MainTask not found"}, status=status.HTTP_404_NOT_FOUND)
        except Subtask.DoesNotExist:
            return Response({"error": "Subtask not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)