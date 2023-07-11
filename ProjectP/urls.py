from django.urls import path
from ProjectP.views.summaryGPT import SummaryGPT
from ProjectP.views.SummaryResultView import SummaryResultView

urlpatterns = [
    path('', SummaryGPT.as_view(), name='generate_summary'),
    path('summary-result/', SummaryResultView.as_view(), name='summary_result'),
]