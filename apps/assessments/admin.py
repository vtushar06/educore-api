from django.contrib import admin

from .models import Attempt, Question, Quiz

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    ordering = ("order",)
    fields = ("text", "question_type", "choices", "correct_answer", "points", "order")

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "passing_score", "max_attempts", "time_limit_minutes")
    list_filter = ("passing_score", "max_attempts")
    search_fields = ("title", "lesson__title")
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_preview", "quiz", "question_type", "points", "order")
    list_filter = ("question_type", "quiz")

    @admin.display(description="Question")
    def text_preview(self, obj):
        return obj.text[:80] + "..." if len(obj.text) > 80 else obj.text

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "score", "passed", "started_at", "time_taken_seconds")
    list_filter = ("passed", "quiz", "started_at")
    search_fields = ("student__email", "quiz__title")
    readonly_fields = (
        "student",
        "quiz",
        "answers",
        "score",
        "passed",
        "started_at",
        "completed_at",
        "time_taken_seconds",
    )

    def has_add_permission(self, request):
        return False
