from django.contrib import admin

from .models import Course, Enrollment, Lesson, LessonProgress, Module


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    ordering = ("order",)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ("order",)
    fields = ("title", "duration_minutes", "order", "video_url")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "instructor", "category", "difficulty", "is_published", "created_at")
    list_filter = ("is_published", "difficulty", "category", "created_at")
    search_fields = ("title", "description", "instructor__email")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ModuleInline]
    list_editable = ("is_published",)
    date_hierarchy = "created_at"


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "duration_minutes", "order")
    list_filter = ("module__course",)
    search_fields = ("title",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "course",
        "status",
        "enrolled_at",
        "get_completion",
    )
    list_filter = ("status", "course", "enrolled_at")
    search_fields = ("student__email", "course__title")
    list_editable = ("status",)
    actions = ["approve_enrollments", "reject_enrollments"]

    @admin.display(description="Completion %")
    def get_completion(self, obj):
        return f"{obj.completion_percentage}%"

    @admin.action(description="Approve selected enrollments")
    def approve_enrollments(self, request, queryset):
        updated = queryset.filter(status="pending").update(status="approved")
        self.message_user(request, f"{updated} enrollment(s) approved.")

    @admin.action(description="Reject selected enrollments")
    def reject_enrollments(self, request, queryset):
        updated = queryset.filter(status="pending").update(status="rejected")
        self.message_user(request, f"{updated} enrollment(s) rejected.")


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "lesson", "completed_at")
    list_filter = ("completed_at",)
    readonly_fields = ("enrollment", "lesson", "completed_at")
