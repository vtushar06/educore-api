import pytest
from django.contrib.auth import get_user_model

from apps.courses.models import Course, Enrollment, Lesson, LessonProgress, Module

User = get_user_model()


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
        title="Python Fundamentals",
        description="Learn Python from scratch",
        instructor=instructor,
        category="Programming",
        difficulty="beginner",
        is_published=True,
    )


@pytest.fixture
def module(course):
    return Module.objects.create(course=course, title="Getting Started", order=1)


@pytest.fixture
def lesson(module):
    return Lesson.objects.create(
        module=module,
        title="Introduction",
        content="Welcome to the course.",
        order=1,
    )


@pytest.mark.django_db
class TestCourseModel:
    def test_auto_slug_generation(self, course):
        assert course.slug == "python-fundamentals"

    def test_duplicate_slug_increments(self, instructor):
        Course.objects.create(
            title="Python Fundamentals",
            description="Another one",
            instructor=instructor,
            category="Programming",
        )
        c2 = Course.objects.create(
            title="Python Fundamentals",
            description="Yet another",
            instructor=instructor,
            category="Programming",
        )
        assert c2.slug == "python-fundamentals-1"

    def test_total_lessons(self, course, lesson):
        assert course.total_lessons == 1

    def test_course_str(self, course):
        assert str(course) == "Python Fundamentals"


@pytest.mark.django_db
class TestEnrollmentModel:
    def test_default_status_is_pending(self, student, course):
        enrollment = Enrollment.objects.create(student=student, course=course)
        assert enrollment.status == "pending"

    def test_completion_percentage(self, student, course, module, lesson):
        enrollment = Enrollment.objects.create(
            student=student, course=course, status="approved"
        )
        assert enrollment.completion_percentage == 0

        LessonProgress.objects.create(enrollment=enrollment, lesson=lesson)
        assert enrollment.completion_percentage == 100.0

    def test_unique_enrollment(self, student, course):
        Enrollment.objects.create(student=student, course=course)
        with pytest.raises(Exception):
            Enrollment.objects.create(student=student, course=course)
