from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Quiz(models.Model):
    """
    Assessment attached to a specific lesson.
    Each lesson can have at most one quiz.
    """

    lesson = models.OneToOneField("courses.Lesson", on_delete=models.CASCADE, related_name="quiz")
    title = models.CharField(max_length=200)
    passing_score = models.PositiveIntegerField(
        default=60,
        help_text="Minimum percentage to pass.",
        validators=[MinValueValidator(1)],
    )
    max_attempts = models.PositiveIntegerField(
        default=3,
        help_text="Maximum number of attempts allowed. 0 = unlimited.",
    )
    time_limit_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Time limit in minutes. Leave blank for no limit.",
    )

    class Meta:
        verbose_name = "quiz"
        verbose_name_plural = "quizzes"

    def __str__(self):
        return f"Quiz: {self.title}"


class Question(models.Model):
    """
    A question within a quiz. Supports MCQ and short-answer types.

    For MCQ, `choices` stores a list of dicts:
        [{"text": "Option A", "is_correct": true}, ...]

    For short_answer, `correct_answer` stores the expected text.
    """

    class QuestionType(models.TextChoices):
        MCQ = "mcq", "Multiple Choice"
        SHORT_ANSWER = "short_answer", "Short Answer"

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MCQ,
    )
    choices = models.JSONField(
        null=True,
        blank=True,
        help_text='MCQ options as [{"text": "...", "is_correct": false}, ...]',
    )
    correct_answer = models.TextField(
        blank=True,
        help_text="Expected answer for short-answer questions.",
    )
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "question"

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"


class Attempt(models.Model):
    """
    Records a student's attempt at a quiz.

    `answers` stores the student's responses:
        [{"question_id": 1, "answer": "B"}, ...]
    """

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    answers = models.JSONField(default=list, blank=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score as a percentage.",
    )
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_taken_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "attempt"

    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"{self.student.email} — {self.quiz.title} [{status}]"
