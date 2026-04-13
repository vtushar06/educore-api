import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

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
def course(instructor):
    return Course.objects.create(
        title="Django Mastery",
        description="Master Django and DRF",
        instructor=instructor,
        category="Web Development",
        is_published=True,
    )


@pytest.fixture
def module(course):
    return Module.objects.create(course=course, title="Intro", order=1)


@pytest.fixture
def lesson(module):
    return Lesson.objects.create(module=module, title="First Lesson", content="Hello", order=1)


@pytest.mark.django_db
class TestCourseEndpoints:
    def test_list_courses_public(self, api_client, course):
        url = reverse("courses:course-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_create_course_requires_instructor(self, api_client, student):
        api_client.force_authenticate(user=student)
        url = reverse("courses:course-list")
        response = api_client.post(
            url,
            {"title": "Unauthorized", "description": "Nope", "category": "Test"},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_course_as_instructor(self, api_client, instructor):
        api_client.force_authenticate(user=instructor)
        url = reverse("courses:course-list")
        response = api_client.post(
            url,
            {"title": "New Course", "description": "Brand new", "category": "Tech"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestEnrollmentEndpoints:
    def test_enroll_as_student(self, api_client, student, course):
        api_client.force_authenticate(user=student)
        url = reverse("courses:course-enroll", kwargs={"slug": course.slug})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == "pending"

    def test_duplicate_enrollment_blocked(self, api_client, student, course):
        api_client.force_authenticate(user=student)
        url = reverse("courses:course-enroll", kwargs={"slug": course.slug})
        api_client.post(url)
        response = api_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_complete_lesson(self, api_client, student, course, lesson):
        api_client.force_authenticate(user=student)
        Enrollment.objects.create(student=student, course=course, status="approved")
        url = reverse("courses:lesson-complete", kwargs={"pk": lesson.pk})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
