import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def student_user():
    return User.objects.create_user(
        email="student@test.com",
        password="TestPass123!",
        first_name="Test",
        last_name="Student",
    )

@pytest.mark.django_db
class TestRegistration:
    def test_register_student(self, api_client):
        url = reverse("accounts:register")
        data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "StrongPass99!",
            "password_confirm": "StrongPass99!",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["role"] == "student"

    def test_register_password_mismatch(self, api_client):
        url = reverse("accounts:register")
        data = {
            "email": "bad@example.com",
            "first_name": "Bad",
            "last_name": "User",
            "password": "StrongPass99!",
            "password_confirm": "WrongPass99!",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_admin_blocked(self, api_client):
        url = reverse("accounts:register")
        data = {
            "email": "hacker@example.com",
            "first_name": "Hack",
            "last_name": "Er",
            "password": "StrongPass99!",
            "password_confirm": "StrongPass99!",
            "role": "admin",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.django_db
class TestAuthentication:
    def test_login_returns_tokens(self, api_client, student_user):
        url = reverse("accounts:login")
        response = api_client.post(
            url,
            {"email": "student@test.com", "password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_profile_requires_auth(self, api_client):
        url = reverse("accounts:profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_returns_user_data(self, api_client, student_user):
        api_client.force_authenticate(user=student_user)
        url = reverse("accounts:profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "student@test.com"
