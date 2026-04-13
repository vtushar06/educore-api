"""
Content signals — auto-issue certificates on course completion.

Listens to LessonProgress creation and checks whether the student
has now completed all lessons in the course. If so, a Certificate
is issued automatically.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="courses.LessonProgress")
def check_course_completion(sender, instance, created, **kwargs):
    """Issue a certificate when a student reaches 100% completion."""
    if not created:
        return

    enrollment = instance.enrollment

    if enrollment.completion_percentage < 100:
        return

    from .models import Certificate

    cert, was_created = Certificate.objects.get_or_create(
        student=enrollment.student,
        course=enrollment.course,
    )

    if was_created:
        logger.info(
            "Certificate issued: %s for '%s' (ID: %s)",
            enrollment.student.email,
            enrollment.course.title,
            cert.certificate_id,
        )
