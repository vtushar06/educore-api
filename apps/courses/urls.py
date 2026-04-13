from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    # Courses
    path("courses/", views.CourseListCreateView.as_view(), name="course-list"),
    path("courses/<slug:slug>/", views.CourseDetailView.as_view(), name="course-detail"),
    path("courses/<slug:slug>/enroll/", views.EnrollView.as_view(), name="course-enroll"),
    path(
        "courses/<slug:slug>/modules/",
        views.ModuleListCreateView.as_view(),
        name="module-list",
    ),
    # Lessons
    path(
        "modules/<int:module_id>/lessons/",
        views.LessonListCreateView.as_view(),
        name="lesson-list",
    ),
    path("lessons/<int:pk>/", views.LessonDetailView.as_view(), name="lesson-detail"),
    path(
        "lessons/<int:pk>/complete/",
        views.LessonCompleteView.as_view(),
        name="lesson-complete",
    ),
    # Enrollments
    path("enrollments/", views.EnrollmentListView.as_view(), name="enrollment-list"),
    path(
        "enrollments/<int:pk>/",
        views.EnrollmentUpdateView.as_view(),
        name="enrollment-update",
    ),
    path(
        "my-enrollments/",
        views.MyEnrollmentsView.as_view(),
        name="my-enrollments",
    ),
]
