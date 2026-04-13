import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.content.models import Certificate, Note, Review
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
def course_setup(instructor, student):
    course = Course.objects.create(
        title="Review Course",
        description="Course for testing reviews",
        instructor=instructor,
        category="Testing",
        is_published=True,
    )
    module = Module.objects.create(course=course, title="Mod1", order=1)
    lesson = Lesson.objects.create(
        module=module, title="Lesson 1", content="Hello", order=1
    )
    enrollment = Enrollment.objects.create(
        student=student, course=course, status="approved"
    )
    return {"course": course, "lesson": lesson, "enrollment": enrollment}


@pytest.mark.django_db
class TestNotes:
    def test_create_note(self, api_client, student, course_setup):
        api_client.force_authenticate(user=student)
        lesson = course_setup["lesson"]
        url = reverse("content:note-list", kwargs={"lesson_id": lesson.pk})
        response = api_client.post(
            url, {"body": "My private note"}, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Note.objects.filter(author=student).count() == 1

    def test_notes_are_private(self, api_client, course_setup):
        lesson = course_setup["lesson"]
        other_student = User.objects.create_user(
            email="other@test.com", password="Pass123!"
        )
        Note.objects.create(
            author=other_student, lesson=lesson, body="Other's note"
        )

        api_client.force_authenticate(
            user=User.objects.create_user(
                email="viewer@test.com", password="Pass123!"
            )
        )
        url = reverse("content:note-list", kwargs={"lesson_id": lesson.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0


@pytest.mark.django_db
class TestReviews:
    def test_create_review_with_enrollment(self, api_client, student, course_setup):
        api_client.force_authenticate(user=student)
        course = course_setup["course"]
        url = reverse("content:review-list", kwargs={"slug": course.slug})
        response = api_client.post(
            url, {"rating": 5, "comment": "Great course!"}, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_review_without_enrollment_blocked(self, api_client, course_setup):
        unenrolled = User.objects.create_user(
            email="unenrolled@test.com", password="Pass123!"
        )
        api_client.force_authenticate(user=unenrolled)
        course = course_setup["course"]
        url = reverse("content:review-list", kwargs={"slug": course.slug})
        response = api_client.post(
            url, {"rating": 5, "comment": "Can't review"}, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reviews_are_public(self, api_client, student, course_setup):
        course = course_setup["course"]
        Review.objects.create(student=student, course=course, rating=4, comment="Good")
        url = reverse("content:review-list", kwargs={"slug": course.slug})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1


@pytest.mark.django_db
class TestCertificates:
    def test_certificate_verification(self, api_client, student, course_setup):
        course = course_setup["course"]
        cert = Certificate.objects.create(student=student, course=course)
        url = reverse(
            "content:certificate-verify",
            kwargs={"certificate_id": cert.certificate_id},
        )
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["student"]["email"] == student.email
