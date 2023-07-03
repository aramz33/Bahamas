from django.db import models


class Transcription(models.Model):
    audio_file = models.FileField(upload_to='static/audio/')
    transcription = models.TextField(max_length=1000)

    def __str__(self):
        return self.audio_file.name

# Create your models here.
