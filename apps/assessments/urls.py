from django.urls import path

from . import views

app_name = "assessments"

urlpatterns = [
    path(
        "lessons/<int:lesson_id>/quiz/",
        views.QuizDetailView.as_view(),
        name="quiz-detail",
    ),
    path(
        "lessons/<int:lesson_id>/quiz/create/",
        views.QuizCreateView.as_view(),
        name="quiz-create",
    ),
    path(
        "quizzes/<int:quiz_id>/attempt/",
        views.AttemptCreateView.as_view(),
        name="attempt-create",
    ),
    path(
        "quizzes/<int:quiz_id>/attempts/",
        views.AttemptListView.as_view(),
        name="attempt-list",
    ),
]
