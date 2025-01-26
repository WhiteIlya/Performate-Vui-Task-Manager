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

from .models import MainTask

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