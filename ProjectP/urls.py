from django.urls import path
from ProjectP.views.summaryGPT import SummaryGPT

urlpatterns = [
    path('', SummaryGPT.as_view(), name='summaryGPT'),
]