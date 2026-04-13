from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions

from apps.accounts.permissions import IsOwnerOrReadOnly
from apps.courses.models import Course

from .models import Certificate, Note, Review
from .serializers import (
    CertificateSerializer,
    NoteCreateSerializer,
    NoteSerializer,
    ReviewCreateSerializer,
    ReviewSerializer,
)


# ---------------------------------------------------------------------------
# Notes (private, per-lesson)
# ---------------------------------------------------------------------------


class NoteListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/lessons/{lesson_id}/notes/  — list own notes for a lesson
    POST /api/v1/lessons/{lesson_id}/notes/  — create a note
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return NoteCreateSerializer
        return NoteSerializer

    def get_queryset(self):
        return Note.objects.filter(
            author=self.request.user,
            lesson_id=self.kwargs["lesson_id"],
        )


class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/v1/notes/{id}/  — manage own note
    """

    serializer_class = NoteSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        return Note.objects.filter(author=self.request.user)


# ---------------------------------------------------------------------------
# Reviews (one per enrollment)
# ---------------------------------------------------------------------------


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/courses/{slug}/reviews/  — public reviews for a course
    POST /api/v1/courses/{slug}/reviews/  — submit a review (enrolled only)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(
            course__slug=self.kwargs["slug"]
        ).select_related("student")


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/DELETE /api/v1/reviews/{id}/
    """

    serializer_class = ReviewSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    queryset = Review.objects.all()


# ---------------------------------------------------------------------------
# Certificates
# ---------------------------------------------------------------------------


class MyCertificatesView(generics.ListAPIView):
    """
    GET /api/v1/my-certificates/

    List certificates earned by the authenticated user.
    """

    serializer_class = CertificateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Certificate.objects.filter(
            student=self.request.user
        ).select_related("course")


class CertificateVerifyView(generics.RetrieveAPIView):
    """
    GET /api/v1/certificates/{uuid}/

    Public endpoint for certificate verification.
    """

    serializer_class = CertificateSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = Certificate.objects.select_related("student", "course")
    lookup_field = "certificate_id"
