from django.urls import path
from .views import FinalDecisionView, EditorDashboardView
from .views import (
    SubmitPaperView,
    TrackPaperView,
    AssignReviewersView,
    UpdateStatusView,
    UserDashboardView,
    ReviewerDashboardView,
    SubmitReviewView,
    EditorDashboardView,
    FinalDecisionView

)

urlpatterns = [
    path('submit/', SubmitPaperView.as_view()),
    path('track/', TrackPaperView.as_view()),
    path('assign-reviewers/<int:manuscript_id>/', AssignReviewersView.as_view()),
    path('update-status/<int:pk>/', UpdateStatusView.as_view()),
    path('dashboard/', UserDashboardView.as_view()),
    path('reviewer/dashboard/', ReviewerDashboardView.as_view()),
    path('reviewer/submit-review/<int:review_id>/', SubmitReviewView.as_view()),
    path('editor/dashboard/', EditorDashboardView.as_view()),
    path('editor/final-decision/<int:manuscript_id>/', FinalDecisionView.as_view()),

]