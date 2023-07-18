
import os
import openai
from django.shortcuts import render
from docx import Document
from django.shortcuts import redirect
from django.views import View


API_KEY = os.getenv("API_KEY")  # Access the API key from environment variable in config.env

class SummaryGPT(View):
    @staticmethod
    def get(request):
        return render(request, 'upload.html')

    def post(self, request):
        text_inputs = request.POST.getlist('text')
        types = request.POST.getlist('type')
        doc_files = request.FILES.getlist('video')

        if types == ["None"]:
            types = ['']

        if text_inputs or doc_files:
            summary = self.generate_summary(text_inputs, types, doc_files)
            if summary:
                return redirect('summary_result')
            else:
                return render(request, 'upload.html', {'error': 'Failed to generate summary.'})

        return render(request, 'upload.html', {'error': 'No file or text input provided.'})

    @staticmethod
    def generate_summary(text_inputs, types, doc_files):

        openai.api_key = API_KEY
        system_content = "You are a professional assistant for a digital development company called 'The Amazingfull " \
                         "Circus', with one job: summarize the following input and " \
                         "highlight the " \
                         "most important points under bullet points but still make full sentences, as if you were " \
                         "using the input to build a project proposal contract. You will get " \
                         "text inputs. If information is repeated in multiple " \
                         "text inputs, try not repeat it to much, or rephrase it. Each " \
                         "text input is going to indicate beforehand what kind of input it is: a PDF summary, " \
                         "a general conversation, a video meeting transcription or an email. Take that into account " \
                         "when " \
                         "analysing the text inputs. If you get different spellings, always choose the spelling that " \
                         "is provided in an email, a pdf summary or a general text before the ones coming from a " \
                         "a video meeting transcription. \n\nYour response should be organized " \
                         "" \
                         "as follows: \n\n\1. Project " \
                         "description\n\n 2. Goal\n\n3. Objectives \n\n 4. Methodology \n\n 5. Scope \n\n 6. " \
                         "Deliverables " \
                         "\n\n 7. Timeline \n\n 8. Budget \n\n 9. Risks \n\n 10. Conclusion. \n\n You can add some " \
                         "analysis regarding missing information " \
                         "in each section\n\nYou should also include a list of references at the " \
                         "end of the summary.\n\n. Watch out for proper nouns and acronyms. Document names should be " \
                         "a good source for company names. Don't trust video meeting transcriptions for proper nouns " \
                         "orthography \n\n"

        messages = [
            {"role": "system", "content": system_content},
        ]

        for idx, doc_file in enumerate(doc_files):
            doc = Document(doc_file)
            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + " "  # Append each paragraph's text with a space
            document_name = doc_file.name
            message_type = f"Video Meeting Transcription {idx + 1} - Document name: {document_name}"
            messages.append({"role": "user", "content": f"{message_type}: {text_content}"})

        if text_inputs != [''] and types != ['']:
            for idx, text_input in enumerate(text_inputs):
                message_type = types[idx]
                messages.append({"role": "user", "content": f"{message_type}: {text_input}"})

        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            temperature=0.5,
        )

        from ProjectP.models import Summary

        if completion.choices and completion.choices[0].message:
            system_content = completion.choices[0].message.content
            summary = Summary(content=system_content)
            summary.save()
            return system_content

        return None

