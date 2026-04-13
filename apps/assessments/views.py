from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsEnrolled, IsInstructorOrAdmin
from apps.courses.models import Enrollment, Lesson

from .models import Attempt, Quiz
from .serializers import (
    AttemptSerializer,
    AttemptSubmitSerializer,
    QuizCreateSerializer,
    QuizSerializer,
)

class QuizDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/lessons/{lesson_id}/quiz/

    Retrieve the quiz attached to a lesson.
    """

    serializer_class = QuizSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        lesson = get_object_or_404(Lesson, pk=self.kwargs["lesson_id"])
        return get_object_or_404(Quiz, lesson=lesson)

class QuizCreateView(generics.CreateAPIView):
    """
    POST /api/v1/lessons/{lesson_id}/quiz/

    Create a quiz for a lesson (instructor only).
    """

    serializer_class = QuizCreateSerializer
    permission_classes = (IsInstructorOrAdmin,)

    def perform_create(self, serializer):
        lesson = get_object_or_404(Lesson, pk=self.kwargs["lesson_id"])
        if hasattr(lesson, "quiz"):
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"detail": "This lesson already has a quiz."})
        serializer.save(lesson=lesson)

class AttemptCreateView(APIView):
    """
    POST /api/v1/quizzes/{quiz_id}/attempt/

    Submit answers and get the quiz graded.
    Enforces max retake limit.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        course = quiz.lesson.module.course

        # Verify enrollment
        enrolled = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status=Enrollment.Status.APPROVED,
        ).exists()

        if not enrolled and request.user.role not in ("instructor", "admin"):
            return Response(
                {"detail": "You must be enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Check retake limit
        if quiz.max_attempts > 0:
            attempt_count = Attempt.objects.filter(
                student=request.user, quiz=quiz
            ).count()
            if attempt_count >= quiz.max_attempts:
                return Response(
                    {
                        "detail": f"Maximum attempts ({quiz.max_attempts}) reached.",
                        "attempts_used": attempt_count,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = AttemptSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attempt = serializer.grade(quiz=quiz, student=request.user)

        return Response(
            AttemptSerializer(attempt).data,
            status=status.HTTP_201_CREATED,
        )

class AttemptListView(generics.ListAPIView):
    """
    GET /api/v1/quizzes/{quiz_id}/attempts/

    Students see their own attempts. Instructors see all attempts.
    """

    serializer_class = AttemptSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        quiz_id = self.kwargs["quiz_id"]
        qs = Attempt.objects.filter(quiz_id=quiz_id).select_related("student")

        if self.request.user.role in ("instructor", "admin"):
            return qs
        return qs.filter(student=self.request.user)
