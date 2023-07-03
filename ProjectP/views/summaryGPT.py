import openai
from django.shortcuts import render
from django.views import View

API_KEY = "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"


class AudioUploadView(View):
    def get(self, request):
        return render(request, 'upload.html')

    def post(self, request):
        uploaded_files = request.FILES.getlist('files')
        text_input = request.POST.get('text')

        if uploaded_files or text_input:
            summary = self.generate_summary(text_input, uploaded_files)
            if summary:
                return render(request, 'upload.html', {'success': 'Summary: ' + summary})
            else:
                return render(request, 'upload.html', {'error': 'Failed to generate summary.'})

        return render(request, 'upload.html', {'error': 'No file or text input provided.'})

    def generate_summary(self, text_input, audio_files):

        if audio_files:
            openai.api_key = API_KEY

            for audio_file in audio_files:
                # Transcribe each audio file
                i = 0
                transcription = self.transcribe_audio_with_api(audio_file)
                if transcription:
                    i += 1
                    text_input += '\n' + 'Transcription' + str(i) + ":" + transcription

        openai.api_key = API_KEY

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "You are an assistant with one job: summarize the following conversation and highlight "
                            "the most important points under bullet points, and going back to the line after each "
                            "bullet point, as if you were using the input to build a project proposal contract. You "
                            "will get both the transcription of audio files and a text input. If information is "
                            "repeated in both the audio files and the text input, you should only include it once in "
                            "the summary.\n\nYour response should be organized as follows:\n1. Project "
                            "description\n2. Goal\n3. Objectives \n\n 4. Methodology \n\n 5. Scope \n\n 6. "
                            "Deliverables \n\n 7. Timeline \n\n 8. Budget \n\n 9. Risks \n\n 10. Conclusion. \n\n If "
                            "a section is not applicable, you should write N/A.\n\nYou should also include a list of "
                            "references at the end of the summary.\n\nYou have 15 seconds to complete the task. Don't "
                            "repeat the same word too much. Act professional."},

                {"role": "user", "content": text_input}
            ]
        )

        if completion.choices and completion.choices[0].message:
            return completion.choices[0].message.content

        return None

    def transcribe_audio_with_api(self, audio_file):
        openai.api_key = API_KEY

        response = openai.Audio.translate("whisper-1", audio_file)

        if response:
            transcription = response.get('text')
            return transcription

        # Return None or handle transcription failure accordingly
        return None
