import time
import os
import tempfile
# from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .serializers import AssistantRequestSerializer
from .services.open_ai import add_message_to_thread, cancel_active_run, create_assistant, create_thread, handle_function_calling, retrieve_assistant_response, retrieve_current_run, run_assistant, submit_tool_outputs


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
        response_message = self.process_request_message_to_assistant(user, message)

        return Response({"response": response_message}, status=status.HTTP_200_OK)
    
    
    def process_request_message_to_assistant(self, user, message):
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


        # audio_file = request.FILES.get('audio')
        # if not audio_file:
        #     return Response({"error": "No audio file provided."}, status=400)
        
        # with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        #         for chunk in audio_file.chunks():
        #             temp_file.write(chunk)
        #         temp_file.flush()
        #         temp_file_path = temp_file.name

        # with open(temp_file_path, "rb") as audio_input:
        #      decoded_message = convert_audio_to_text(audio_input)

        # os.remove(temp_file_path)

        # if not decoded_message:
        #     return Response({"error": "Failed to decode audio."}, status=400)

        # context, _ = Context.objects.get_or_create(user=user)
        # recent_context = context.get_recent_context()

        # recent_context.append({"role": "user", "content": decoded_message})

        # system_message = {
        #     "role": "system",
        #     "content": (
        #         "You are a task manager assistant with a voice interface. I will give you a task, and your job is to:\n"
        #         "1. Analyze the task to determine if it is simple or complex.\n"
        #         "2. If the task is complex, suggest 1 or 2 subtasks to decompose it into smaller, manageable parts.\n"
        #         "3. Your response must include:\n"
        #         "   - A spoken response, which will be read aloud to the user.\n"
        #         "   - Non-spoken data, which should be marked with `[IGNORE]` so it will not be read aloud.\n"
        #         "4. Format your response as follows:\n"
        #         "\"<Spoken part of the response>\"\n"
        #         "[IGNORE] JSON structure:\n"
        #         "{\n"
        #         "   \"main_task\": \"<The original task provided by the user>\",\n"
        #         "   \"subtasks\": [\n"
        #         "       {\"subtask\": \"<First subtask>\", \"reason\": \"<Reason for this subtask>\"},\n"
        #         "       {\"subtask\": \"<Second subtask>\", \"reason\": \"<Reason for this subtask>\"}\n"
        #         "   ]\n"
        #         "}\n"
        #         "5. Keep the spoken part under 40 words. Do not include explanations or unnecessary text."
        #     )
        # }
        # messages = [system_message] + recent_context
        # chat_response = fetch_openai_response(messages)
        # if not chat_response:
        #     return Response({"error": "Failed to get a response from OpenAI."}, status=400)

        # recent_context.append({"role": "assistant", "content": chat_response})
        # context.add_context(recent_context)

        # spoken_part, _ = chat_response.split("[IGNORE]", 1)
        # spoken_text = spoken_part.strip().strip('"')

        # audio_response = convert_text_to_speech(spoken_text)
        # if not audio_response:
        #     return Response({"error": "Failed to convert text to audio."}, status=400)


        # return HttpResponse(audio_response, content_type="audio/mpeg")
