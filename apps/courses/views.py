from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsInstructorOrAdmin, IsOwnerOrReadOnly

from .models import Course, Enrollment, Lesson, LessonProgress, Module
from .serializers import (
    CourseCreateSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    EnrollmentSerializer,
    LessonProgressSerializer,
    LessonSerializer,
    ModuleCreateSerializer,
    ModuleSerializer,
)


class CourseListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/courses/           — list published courses (public)
    POST /api/v1/courses/           — create a course (instructor/admin)
    """

    queryset = Course.objects.filter(is_published=True)
    filterset_fields = ["category", "difficulty"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "title"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsInstructorOrAdmin()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CourseCreateSerializer
        return CourseListSerializer

    def get_queryset(self):
        qs = Course.objects.all()
        # Instructors/admins see their own unpublished courses too
        if self.request.user.is_authenticated and self.request.user.role in (
            "instructor",
            "admin",
        ):
            return qs
        return qs.filter(is_published=True)


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/v1/courses/{slug}/   — course detail (public for published)
    PUT    /api/v1/courses/{slug}/   — update (owner instructor)
    DELETE /api/v1/courses/{slug}/   — delete (admin only)
    """

    queryset = Course.objects.all()
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        if self.request.method == "DELETE":
            from apps.accounts.permissions import IsAdmin

            return [IsAdmin()]
        return [IsInstructorOrAdmin(), IsOwnerOrReadOnly()]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return CourseCreateSerializer
        return CourseDetailSerializer


class ModuleListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/courses/{slug}/modules/
    POST /api/v1/courses/{slug}/modules/
    """

    def get_course(self):
        return get_object_or_404(Course, slug=self.kwargs["slug"])

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsInstructorOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ModuleCreateSerializer
        return ModuleSerializer

    def get_queryset(self):
        return Module.objects.filter(course__slug=self.kwargs["slug"])

    def perform_create(self, serializer):
        course = self.get_course()
        serializer.save(course=course)


class LessonListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/modules/{module_id}/lessons/
    POST /api/v1/modules/{module_id}/lessons/
    """

    serializer_class = LessonSerializer

    def get_module(self):
        return get_object_or_404(Module, pk=self.kwargs["module_id"])

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsInstructorOrAdmin()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Lesson.objects.filter(module_id=self.kwargs["module_id"])

    def perform_create(self, serializer):
        module = self.get_module()
        serializer.save(module=module)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/v1/lessons/{id}/
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [IsInstructorOrAdmin()]


class LessonCompleteView(APIView):
    """
    POST /api/v1/lessons/{id}/complete/

    Mark a lesson as completed for the authenticated student's enrollment.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        course = lesson.module.course

        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status=Enrollment.Status.APPROVED,
        ).first()

        if not enrollment:
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        progress, created = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)

        if not created:
            return Response(
                {"detail": "Lesson already marked as completed."},
                status=status.HTTP_200_OK,
            )

        return Response(
            LessonProgressSerializer(progress).data,
            status=status.HTTP_201_CREATED,
        )


class EnrollView(APIView):
    """
    POST /api/v1/courses/{slug}/enroll/

    Request enrollment in a course. Creates a pending enrollment.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, is_published=True)

        if request.user.role != "student":
            return Response(
                {"detail": "Only students can enroll in courses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return Response(
                {"detail": "You have already requested enrollment."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        enrollment = Enrollment.objects.create(student=request.user, course=course)
        return Response(
            EnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )


class EnrollmentListView(generics.ListAPIView):
    """
    GET /api/v1/enrollments/

    Instructors see enrollments for their courses.
    Admins see all enrollments.
    """

    serializer_class = EnrollmentSerializer
    permission_classes = (IsInstructorOrAdmin,)
    filterset_fields = ["status", "course"]

    def get_queryset(self):
        user = self.request.user
        qs = Enrollment.objects.select_related("student", "course")
        if user.role == "instructor":
            return qs.filter(course__instructor=user)
        return qs


class EnrollmentUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/v1/enrollments/{id}/

    Approve or reject an enrollment.
    """

    serializer_class = EnrollmentSerializer
    permission_classes = (IsInstructorOrAdmin,)
    queryset = Enrollment.objects.all()

    def get_queryset(self):
        user = self.request.user
        qs = Enrollment.objects.select_related("student", "course")
        if user.role == "instructor":
            return qs.filter(course__instructor=user)
        return qs


class MyEnrollmentsView(generics.ListAPIView):
    """
    GET /api/v1/my-enrollments/

    List the authenticated student's enrollments with progress.
    """

    serializer_class = EnrollmentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related("course")
