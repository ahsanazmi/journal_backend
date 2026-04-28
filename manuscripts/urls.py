from django.urls import path
from .views import (
    SubmitPaperView,
    TrackPaperView,
    SubmitReviewView,
    FinalDecisionView,
)

urlpatterns = [
    path('submit/', SubmitPaperView.as_view()),
    path('track/', TrackPaperView.as_view()),
    
    # Admin endpoints
    path('admin/submit-review/', SubmitReviewView.as_view()),
    path('admin/final-decision/<int:manuscript_id>/', FinalDecisionView.as_view()),
]