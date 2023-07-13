from django.shortcuts import render
from django.views import View
import openai
import os
from dotenv import load_dotenv


dotenv_path = 'config.env'
load_dotenv(dotenv_path)
API_KEY = os.getenv("API_KEY")  # Access the API key from environment variable in config.env
class SummaryResultView(View):
    @staticmethod
    def get(request):
        from ProjectP.models import Summary
        summary = Summary.objects.last()  # Assuming the latest summary is the one generated
        if summary:
            return render(request, 'summary_result.html', {'summary': summary.content})
        else:
            return render(request, 'summary_result.html', {'error': 'Summary not found.'})

    def post(self, request):
        from ProjectP.models import Summary
        user_input = request.POST.get('user_input')
        summary = Summary.objects.last()  # Assuming the latest summary is the one generated
        openai.api_key = API_KEY

        if user_input and summary:
            messages = [
                {"role": "assistant", "content": summary.content},
                {"role": "user", "content": user_input},
                {"role": "system", "content": "You have generated a summary previously. the user will input "
                                              "specifications. Rewrite the summary to include these specifications. "
                                              "Don't change the organization of the summary. Always return what "
                                              "hasn't bee changed as well as the new input."}
            ]

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )

            if completion.choices and completion.choices[0].message:
                system_response = completion.choices[0].message.content
                summary = Summary(content=system_response)
                summary.save()
                return render(request, 'summary_result.html', {'summary': summary.content})
            else:
                return render(request, 'summary_result.html', {'summary': summary.content, 'error': 'Failed to generate system response.'})
        else:
            return render(request, 'summary_result.html', {'error': 'Invalid input.'})

