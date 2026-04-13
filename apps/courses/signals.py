"""
Course signals — enrollment status change notifications.

When an enrollment status changes to 'approved', this triggers
an async notification (via Celery if available, otherwise logs).
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Enrollment

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Enrollment)
def enrollment_status_changed(sender, instance, created, **kwargs):
    """
    Notify the student when their enrollment is approved.
    Uses Celery if available, otherwise falls back to logging.
    """
    if created:
        logger.info(
            "New enrollment request: %s → %s",
            instance.student.email,
            instance.course.title,
        )
        return

    # Only fire on status update to approved
    if instance.status != Enrollment.Status.APPROVED:
        return

    try:
        from apps.courses.tasks import send_enrollment_notification

        send_enrollment_notification.delay(instance.pk)
    except ImportError:
        logger.info(
            "Enrollment approved: %s → %s (Celery not configured, skipping email)",
            instance.student.email,
            instance.course.title,
        )
