from django.conf import settings
from django.db import models
from django.utils.text import slugify

class Course(models.Model):
    """
    A course created by an instructor containing ordered modules.
    """

    class Difficulty(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses_taught",
        limit_choices_to={"role": "instructor"},
    )
    category = models.CharField(max_length=100, db_index=True)
    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BEGINNER,
    )
    is_published = models.BooleanField(default=False, db_index=True)
    thumbnail = models.ImageField(upload_to="courses/thumbnails/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "course"
        verbose_name_plural = "courses"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def total_lessons(self):
        return Lesson.objects.filter(module__course=self).count()

    @property
    def average_rating(self):
        from apps.content.models import Review

        avg = Review.objects.filter(course=self).aggregate(
            avg=models.Avg("rating")
        )["avg"]
        return round(avg, 2) if avg else None

class Module(models.Model):
    """An ordered section within a course."""

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="modules"
    )
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("course", "order")
        verbose_name = "module"

    def __str__(self):
        return f"{self.course.title} — {self.title}"

class Lesson(models.Model):
    """Individual lesson/lecture within a module."""

    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Lesson body in Markdown format.")
    video_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = ("module", "order")
        verbose_name = "lesson"

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    """
    Tracks a student's enrollment in a course.

    Workflow: student requests → pending → instructor approves/rejects.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        DROPPED = "dropped", "Dropped"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-enrolled_at"]
        verbose_name = "enrollment"

    def __str__(self):
        return f"{self.student.email} → {self.course.title} ({self.status})"

    @property
    def completion_percentage(self):
        total = self.course.total_lessons
        if total == 0:
            return 0
        completed = self.progress.count()
        return round((completed / total) * 100, 1)

class LessonProgress(models.Model):
    """Records a student completing a specific lesson."""

    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="progress"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="completions"
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("enrollment", "lesson")
        verbose_name = "lesson progress"
        verbose_name_plural = "lesson progress"

    def __str__(self):
        return f"{self.enrollment.student.email} completed {self.lesson.title}"
