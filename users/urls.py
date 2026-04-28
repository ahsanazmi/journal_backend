from django.urls import path
from .views import LoginView, ReviewerLoginView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('reviewer-login/', ReviewerLoginView.as_view()),
]