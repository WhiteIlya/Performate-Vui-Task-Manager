import base64
from datetime import timedelta
import time
import os
import tempfile
# from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.files.uploadedfile import UploadedFile
from django.utils.timezone import now
# from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .models import MainTask, Subtask, Notification, VoiceConfig

from .serializers import AssistantRequestSerializer, MainTaskSerializer, NotificationSerializer, VoiceConfigSerializer
from .services.open_ai import (
    add_message_to_thread, 
    cancel_active_run, 
    create_assistant, 
    create_thread, 
    handle_function_calling,
    modify_assistant_instruction, 
    retrieve_assistant_response, 
    retrieve_current_run, 
    run_assistant,
    convert_audio_to_text
)
from .services.eleven_labs import convert_text_to_speech, filter_voices, get_voice_settings, update_voice_settings


class AssistantAPIView(APIView):
    permission_classes = [IsAuthenticated]
    # parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = AssistantRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data["message"]

        user = request.user

        # Check if user has assistant_id and thread_id
        if not user.assistant_id:
            assistant = create_assistant(user)
            thread = create_thread()

            user.assistant_id = assistant.id
            user.thread_id = thread.id
            user.save()
        elif not user.thread_id and user.assistant_id:
            thread = create_thread()
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

            # Check if user has assistant_id and thread_id
            if not user.assistant_id:
                assistant = create_assistant(user)
                thread = create_thread()

                user.assistant_id = assistant.id
                user.thread_id = thread.id
                user.save()
            elif not user.thread_id and user.assistant_id:
                thread = create_thread()
                user.thread_id = thread.id
                user.save()

            response_message = process_request_message_to_assistant(user, text_message)
        except Exception as e:
            return Response({"error": f"Failed to process assistant message: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            audio_response = convert_text_to_speech(user, response_message)
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
    
class NotificationsAPIView(APIView):
    """
    API view to fetch notifications and mark them as read.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user).order_by('is_read')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        notification_id = request.data.get("notification_id")

        if not notification_id:
            return Response({"error": "Notification ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VoiceSelectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        accent = request.data.get("accent")
        gender = request.data.get("gender")
        age = request.data.get("age")
        description = request.data.get("description")
        use_case = request.data.get("use_case")

        voices = filter_voices(accent, gender, age, description, use_case)
        return Response({"voices": voices}, status=status.HTTP_200_OK)
    

class VoiceSettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        voice_id = request.data.get("voice_id")

        if not voice_id:
            return Response({"error": "voice_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        settings_data = get_voice_settings(voice_id)

        if not settings_data:
            return Response({"error": "Failed to retrieve voice settings"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(settings_data, status=status.HTTP_200_OK)
    

class VoiceConfigAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = VoiceConfigSerializer(data=request.data)

        if serializer.is_valid():
            voice_config, created = VoiceConfig.objects.update_or_create(
                user=user,
                defaults=serializer.validated_data
            )

            settings_response = update_voice_settings(
                voice_id=voice_config.voice_id,
                stability=voice_config.stability,
                similarity_boost=voice_config.similarity_boost,
                style=voice_config.style,
                use_speaker_boost=voice_config.use_speaker_boost
            )

            if settings_response.get("status") != "ok":
                return Response({"error": "Failed to update voice settings in ElevenLabs"}, status=status.HTTP_400_BAD_REQUEST)

            if not user.assistant_id or not user.thread_id:
                assistant = create_assistant(user)
                thread = create_thread()

                user.vui_configured = True
                user.assistant_id = assistant.id
                user.thread_id = thread.id
                user.save()
            else:
                modify_assistant_instruction(user)

            return Response({
                "message": "Voice configuration saved and updated in ElevenLabs! Assistant has created.",
                "voice_config": VoiceConfigSerializer(voice_config).data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        user = request.user
        try:
            voice_config = user.voice_config
            serializer = VoiceConfigSerializer(voice_config)
            return Response({"voice_config": serializer.data}, status=status.HTTP_200_OK)
        except VoiceConfig.DoesNotExist:
            return Response({"voice_config": None}, status=status.HTTP_200_OK)