from django.contrib import admin

from .models import Certificate, Note, Review

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("author", "lesson", "body_preview", "updated_at")
    list_filter = ("updated_at",)
    search_fields = ("author__email", "lesson__title", "body")
    readonly_fields = ("author", "lesson", "created_at", "updated_at")

    @admin.display(description="Note")
    def body_preview(self, obj):
        return obj.body[:100] + "..." if len(obj.body) > 100 else obj.body

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "rating", "created_at")
    list_filter = ("rating", "created_at", "course")
    search_fields = ("student__email", "course__title", "comment")
    readonly_fields = ("student", "course", "created_at")

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_id", "student", "course", "issued_at")
    list_filter = ("issued_at", "course")
    search_fields = ("certificate_id", "student__email", "course__title")
    readonly_fields = ("certificate_id", "student", "course", "issued_at")

    def has_add_permission(self, request):
        # Certificates are auto-issued, not manually created
        return False
