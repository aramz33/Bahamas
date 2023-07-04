import random

import openai
from django.shortcuts import render
from django.views import View
from pydub import AudioSegment
import os
from dotenv import load_dotenv

dotenv_path = 'config.env'
load_dotenv(dotenv_path)

API_KEY = os.getenv("API_KEY")  # Access the API key from environment variable


class AudioUploadView(View):
    def get(self, request):
        return render(request, 'upload.html')

    def post(self, request):
        uploaded_files = request.FILES.getlist('files')
        text_inputs = request.POST.getlist('text')
        types = request.POST.getlist('type')

        if uploaded_files or text_inputs:
            summary = self.generate_summary(text_inputs, types, uploaded_files)
            if summary:
                return render(request, 'upload.html', {'success': 'Summary: ' + summary})
            else:
                return render(request, 'upload.html', {'error': 'Failed to generate summary.'})

        return render(request, 'upload.html', {'error': 'No file or text input provided.'})

    def generate_summary(self, text_inputs, types, audio_files):

        if audio_files:
            openai.api_key = API_KEY

            for audio_file in audio_files:
                # Transcribe each audio file
                i = 0
                transcription = self.transcribe_audio_with_api(audio_file)
                if transcription:
                    i += 1
                    text_inputs.append('\n' + transcription)
                    types.append('Transcription' + str(i))

        openai.api_key = API_KEY
        system_content = "You are a professional assistant with one job: summarize the following conversation and " \
                         "highlight the " \
                         "most important points under bullet points but still make full sentences, as if you were " \
                         "using the input to build a project proposal contract. You will get " \
                         "both the transcription of audio files and text inputs. If information is repeated in both " \
                         "the audio files and text inputs, you should only include it once in the summary. Each " \
                         "text input is going to indicate beforehand what kind of input it is: a PDF summary, " \
                         "a general conversation, or a video meeting transcription. Take that into account when " \
                         "analysing the text inputs. \n\nYour response should be organized " \
                         "as follows:On one side a " \
                         "general resume of the input that was given to you, on another \n1. Project " \
                         "description\n2. Goal\n3. Objectives \n\n 4. Methodology \n\n 5. Scope \n\n 6. Deliverables " \
                         "\n\n 7. Timeline \n\n 8. Budget \n\n 9. Risks \n\n 10. Conclusion. \n\n If a section is not " \
                         "applicable, you should write N/A.\n\nYou should also include a list of references at the " \
                         "end of the summary.\n\nYou have 15 seconds to complete the task. Don't repeat the same word " \
                         "too much. Act professional."

        messages = [
            {"role": "system", "content": system_content},
        ]

        for idx, text_input in enumerate(text_inputs):
            message_type = types[idx]
            messages.append({"role": "user", "content": f"{message_type}: {text_input}"})

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        if completion.choices and completion.choices[0].message:
            return completion.choices[0].message.content

        return None

    def transcribe_audio_with_api(self, audio_file):
        openai.api_key = API_KEY

        def convert_to_wav(input_file, output_file):
            audio = AudioSegment.from_file(input_file)
            audio.export(output_file, format='wav')
            return output_file

        output_file = 'static/audio/' + str(random.randint(1, 1000000)) + '.wav'
        audio_wav = convert_to_wav(audio_file, output_file)

        with open(audio_wav, 'rb') as file:
            response = openai.Audio.translate("whisper-1", file)
            if response:
                transcription = response.get('text')
                os.remove(output_file)
                return transcription

        os.remove(output_file)

        # Return None or handle transcription failure accordingly
        return None
