import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            email="student@example.com",
            password="TestPass123!",
            first_name="Jane",
            last_name="Student",
        )
        assert user.email == "student@example.com"
        assert user.role == "student"
        assert user.check_password("TestPass123!")
        assert not user.is_staff

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPass123!",
            first_name="Admin",
            last_name="User",
        )
        assert admin.role == "admin"
        assert admin.is_staff
        assert admin.is_superuser

    def test_email_is_required(self):
        with pytest.raises(ValueError, match="Email address is required"):
            User.objects.create_user(email="", password="TestPass123!")

    def test_user_str_representation(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="John",
            last_name="Doe",
        )
        assert "test@example.com" in str(user)
        assert "John Doe" in str(user)

    def test_role_properties(self):
        student = User.objects.create_user(email="s@example.com", password="Pass123!", role="student")
        instructor = User.objects.create_user(email="i@example.com", password="Pass123!", role="instructor")
        admin = User.objects.create_user(email="a@example.com", password="Pass123!", role="admin")
        assert student.is_student
        assert instructor.is_instructor
        assert admin.is_admin_user
