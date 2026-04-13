from rest_framework import serializers

from apps.accounts.serializers import UserListSerializer
from apps.courses.models import Enrollment

from .models import Certificate, Note, Review

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ("id", "lesson", "body", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ("id", "body", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        validated_data["lesson_id"] = self.context["view"].kwargs["lesson_id"]
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    student = UserListSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ("id", "student", "course", "rating", "comment", "created_at")
        read_only_fields = ("id", "student", "course", "created_at")

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "rating", "comment", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        request = self.context["request"]
        course_slug = self.context["view"].kwargs["slug"]

        from apps.courses.models import Course

        try:
            course = Course.objects.get(slug=course_slug)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found.")

        # Verify approved enrollment
        is_enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status=Enrollment.Status.APPROVED,
        ).exists()

        if not is_enrolled:
            raise serializers.ValidationError(
                "You must be enrolled in this course to leave a review."
            )

        # Check for existing review
        if Review.objects.filter(student=request.user, course=course).exists():
            raise serializers.ValidationError(
                "You have already reviewed this course."
            )

        attrs["_course"] = course
        return attrs

    def create(self, validated_data):
        course = validated_data.pop("_course")
        validated_data["student"] = self.context["request"].user
        validated_data["course"] = course
        return super().create(validated_data)

class CertificateSerializer(serializers.ModelSerializer):
    student = UserListSerializer(read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Certificate
        fields = ("id", "student", "course", "course_title", "certificate_id", "issued_at")
        read_only_fields = fields
