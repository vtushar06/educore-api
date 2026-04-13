from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    # Notes
    path(
        "lessons/<int:lesson_id>/notes/",
        views.NoteListCreateView.as_view(),
        name="note-list",
    ),
    path("notes/<int:pk>/", views.NoteDetailView.as_view(), name="note-detail"),
    # Reviews
    path(
        "courses/<slug:slug>/reviews/",
        views.ReviewListCreateView.as_view(),
        name="review-list",
    ),
    path("reviews/<int:pk>/", views.ReviewDetailView.as_view(), name="review-detail"),
    # Certificates
    path(
        "my-certificates/",
        views.MyCertificatesView.as_view(),
        name="my-certificates",
    ),
    path(
        "certificates/<uuid:certificate_id>/",
        views.CertificateVerifyView.as_view(),
        name="certificate-verify",
    ),
]
