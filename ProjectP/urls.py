from django.urls import path
from ProjectP.views.summaryGPT import AudioUploadView

urlpatterns = [
    path('', AudioUploadView.as_view(), name='audio_upload'),
]