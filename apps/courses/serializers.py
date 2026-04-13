from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.serializers import UserListSerializer

from .models import Course, Enrollment, Lesson, LessonProgress, Module

User = get_user_model()

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "content", "video_url", "duration_minutes", "order")
        read_only_fields = ("id",)

class LessonBriefSerializer(serializers.ModelSerializer):
    """Lightweight lesson representation for module listings."""

    class Meta:
        model = Lesson
        fields = ("id", "title", "duration_minutes", "order")

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonBriefSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ("id", "title", "order", "lessons")
        read_only_fields = ("id",)

class ModuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ("id", "title", "order")
        read_only_fields = ("id",)

class CourseListSerializer(serializers.ModelSerializer):
    instructor = UserListSerializer(read_only=True)
    total_lessons = serializers.IntegerField(read_only=True, source="total_lessons")
    average_rating = serializers.FloatField(read_only=True, source="average_rating")

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "instructor",
            "category",
            "difficulty",
            "is_published",
            "thumbnail",
            "total_lessons",
            "average_rating",
            "created_at",
        )
        read_only_fields = ("id", "slug", "created_at")

class CourseDetailSerializer(serializers.ModelSerializer):
    instructor = UserListSerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    total_lessons = serializers.IntegerField(read_only=True, source="total_lessons")
    average_rating = serializers.FloatField(read_only=True, source="average_rating")

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "instructor",
            "category",
            "difficulty",
            "is_published",
            "thumbnail",
            "modules",
            "total_lessons",
            "average_rating",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "category",
            "difficulty",
            "is_published",
            "thumbnail",
        )
        read_only_fields = ("id", "slug")

    def create(self, validated_data):
        validated_data["instructor"] = self.context["request"].user
        return super().create(validated_data)

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserListSerializer(read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    completion_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Enrollment
        fields = (
            "id",
            "student",
            "course",
            "course_title",
            "status",
            "enrolled_at",
            "completion_percentage",
        )
        read_only_fields = ("id", "student", "course", "enrolled_at")

class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ("id", "course", "status", "enrolled_at")
        read_only_fields = ("id", "course", "status", "enrolled_at")

class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ("id", "lesson", "completed_at")
        read_only_fields = ("id", "completed_at")
