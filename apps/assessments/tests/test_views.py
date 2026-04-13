import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.assessments.models import Attempt, Question, Quiz
from apps.courses.models import Course, Enrollment, Lesson, Module

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def instructor():
    return User.objects.create_user(
        email="instructor@test.com",
        password="TestPass123!",
        first_name="Test",
        last_name="Instructor",
        role="instructor",
    )

@pytest.fixture
def student():
    return User.objects.create_user(
        email="student@test.com",
        password="TestPass123!",
        first_name="Test",
        last_name="Student",
    )

@pytest.fixture
def course_with_quiz(instructor, student):
    course = Course.objects.create(
        title="Quiz Course",
        description="Course with quizzes",
        instructor=instructor,
        category="Testing",
        is_published=True,
    )
    module = Module.objects.create(course=course, title="Module 1", order=1)
    lesson = Lesson.objects.create(
        module=module, title="Lesson 1", content="Content", order=1
    )
    quiz = Quiz.objects.create(
        lesson=lesson,
        title="Test Quiz",
        passing_score=50,
        max_attempts=2,
    )
    Question.objects.create(
        quiz=quiz,
        text="What is 2+2?",
        question_type="mcq",
        choices=[
            {"text": "3", "is_correct": False},
            {"text": "4", "is_correct": True},
            {"text": "5", "is_correct": False},
        ],
        points=1,
        order=1,
    )
    Question.objects.create(
        quiz=quiz,
        text="Capital of France?",
        question_type="short_answer",
        correct_answer="Paris",
        points=1,
        order=2,
    )
    Enrollment.objects.create(student=student, course=course, status="approved")
    return {"course": course, "quiz": quiz, "questions": list(quiz.questions.all())}

@pytest.mark.django_db
class TestQuizAttempt:
    def test_submit_correct_answers(self, api_client, student, course_with_quiz):
        api_client.force_authenticate(user=student)
        quiz = course_with_quiz["quiz"]
        questions = course_with_quiz["questions"]

        url = reverse("assessments:attempt-create", kwargs={"quiz_id": quiz.pk})
        data = {
            "answers": [
                {"question_id": questions[0].pk, "answer": "4"},
                {"question_id": questions[1].pk, "answer": "Paris"},
            ]
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert float(response.data["score"]) == 100.0
        assert response.data["passed"] is True

    def test_submit_wrong_answers(self, api_client, student, course_with_quiz):
        api_client.force_authenticate(user=student)
        quiz = course_with_quiz["quiz"]
        questions = course_with_quiz["questions"]

        url = reverse("assessments:attempt-create", kwargs={"quiz_id": quiz.pk})
        data = {
            "answers": [
                {"question_id": questions[0].pk, "answer": "3"},
                {"question_id": questions[1].pk, "answer": "London"},
            ]
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert float(response.data["score"]) == 0.0
        assert response.data["passed"] is False

    def test_max_attempts_enforced(self, api_client, student, course_with_quiz):
        api_client.force_authenticate(user=student)
        quiz = course_with_quiz["quiz"]
        questions = course_with_quiz["questions"]

        url = reverse("assessments:attempt-create", kwargs={"quiz_id": quiz.pk})
        data = {
            "answers": [
                {"question_id": questions[0].pk, "answer": "4"},
                {"question_id": questions[1].pk, "answer": "Paris"},
            ]
        }

        # Use up all attempts (max_attempts=2)
        api_client.post(url, data, format="json")
        api_client.post(url, data, format="json")

        # Third attempt should fail
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Maximum attempts" in response.data["detail"]
