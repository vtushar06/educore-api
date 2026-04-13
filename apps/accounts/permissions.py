from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Allow access only to users with the admin role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )

class IsInstructor(permissions.BasePermission):
    """Allow access only to users with the instructor role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "instructor"
        )

class IsInstructorOrAdmin(permissions.BasePermission):
    """Allow access to instructors and admins."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ("instructor", "admin")
        )

class IsEnrolled(permissions.BasePermission):
    """
    Allow access only if the user has an approved enrollment
    for the course referenced by the view.

    Views must provide `get_course()` or set `self.course`.
    Falls back to checking the `course_slug` kwarg.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Instructors and admins can always access course content
        if request.user.role in ("instructor", "admin"):
            return True

        course = getattr(view, "course", None)
        if course is None and hasattr(view, "get_course"):
            course = view.get_course()

        if course is None:
            # Try to resolve from URL kwargs
            from apps.courses.models import Course

            slug = view.kwargs.get("course_slug")
            if slug:
                try:
                    course = Course.objects.get(slug=slug)
                except Course.DoesNotExist:
                    return False

        if course is None:
            return False

        from apps.courses.models import Enrollment

        return Enrollment.objects.filter(
            student=request.user,
            course=course,
            status=Enrollment.Status.APPROVED,
        ).exists()

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission: only the owner can modify.
    Expects the object to have an `author` or `student` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        owner = getattr(obj, "author", None) or getattr(obj, "student", None)
        return owner == request.user
