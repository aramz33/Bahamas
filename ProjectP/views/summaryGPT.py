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


class SummaryGPT(View):
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
        system_content = "You are a professional assistant for a digital development company called 'The Amazingfull " \
                         "Circus', with one job: summarize the following input and " \
                         "highlight the " \
                         "most important points under bullet points but still make full sentences, as if you were " \
                         "using the input to build a project proposal contract. You will get " \
                         "both the transcript of audio files and text inputs. If information is repeated in both " \
                         "the audio files and text inputs, you should only include it once in the summary. Each " \
                         "text input is going to indicate beforehand what kind of input it is: a PDF summary, " \
                         "a general conversation, a video meeting transcription or an email. Take that into account " \
                         "when " \
                         "analysing the text inputs. If you get different spellings, always choose the spelling that " \
                         "is provided in an email, a pdf summary or a general text before the ones coming from an " \
                         "audio transcription or a video meeting transcription. \n\nYour response should be organized "\
                         "" \
                         "as follows: \n1. Project " \
                         "description\n2. Goal\n3. Objectives \n\n 4. Methodology \n\n 5. Scope \n\n 6. Deliverables " \
                         "\n\n 7. Timeline \n\n 8. Budget \n\n 9. Risks \n\n 10. Conclusion. \n\n If a section is not " \
                         "applicable, you should write N/A. You can add some analysis regarding missing information " \
                         "in each section\n\nYou should also include a list of references at the " \
                         "end of the summary.\n\n"

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
            messages.append({"role": "assistant", "content": completion.choices[0].message.content})
            return completion.choices[0].message.content

        return None

    def transcribe_audio_with_api(self, audio_file):
        def convert_to_wav(input_file, output_file):
            audio = AudioSegment.from_file(input_file)
            audio.export(output_file, format='wav')
            return output_file

        def transcribe_segment(segment_file):
            with open(segment_file, 'rb') as file:
                response = openai.Audio.translate("whisper-1", file)
                if response:
                    transcription = response.get('text')
                    os.remove(segment_file)
                    return transcription
            os.remove(segment_file)
            return None

        output_file = 'static/audio/' + str(random.randint(1, 1000000)) + '.wav'
        audio_wav = convert_to_wav(audio_file, output_file)

        segment_duration_sec = 60  # Duration of each segment in seconds

        # Create a directory to store the segments
        os.makedirs('segments', exist_ok=True)

        audio = AudioSegment.from_wav(audio_wav)
        file_duration_sec = len(audio) // 1000  # Convert total duration to seconds
        segment_count = int(file_duration_sec / segment_duration_sec) + 1

        transcriptions = []
        for i in range(segment_count):
            start_time_sec = i * segment_duration_sec
            end_time_sec = min((i + 1) * segment_duration_sec, file_duration_sec)
            segment = audio[start_time_sec * 1000:end_time_sec * 1000]  # Convert time to milliseconds

            segment_file = f'segments/segment{i + 1}.wav'
            segment.export(segment_file, format='wav')

            transcription = transcribe_segment(segment_file)
            if transcription:
                transcriptions.append(transcription)

        full_transcription = ' '.join(transcriptions)

        os.remove(audio_wav)
        os.rmdir('segments')

        return full_transcription

