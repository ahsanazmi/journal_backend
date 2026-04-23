from django.urls import path
from .views import (
    SubmitPaperView,
    TrackPaperView,
    AssignReviewersView,
    UpdateStatusView,
    UserDashboardView,
    ReviewerDashboardView
)

urlpatterns = [
    path('submit/', SubmitPaperView.as_view()),
    path('track/', TrackPaperView.as_view()),
    path('assign-reviewers/<int:manuscript_id>/', AssignReviewersView.as_view()),
    path('update-status/<int:pk>/', UpdateStatusView.as_view()),
    path('dashboard/', UserDashboardView.as_view()),
    path('reviewer/dashboard/', ReviewerDashboardView.as_view()),

]