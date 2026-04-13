"""
Celery tasks for the courses app.
"""

import logging

from celery import shared_task
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_enrollment_notification(self, enrollment_id):
    """Send an email notification when enrollment is approved."""
    from .models import Enrollment

    try:
        enrollment = Enrollment.objects.select_related("student", "course").get(pk=enrollment_id)
    except Enrollment.DoesNotExist:
        logger.warning("Enrollment %s not found, skipping notification.", enrollment_id)
        return

    subject = f"Enrollment Approved: {enrollment.course.title}"
    message = (
        f"Hi {enrollment.student.first_name},\n\n"
        f"Your enrollment in '{enrollment.course.title}' has been approved.\n"
        f"You can now access all course materials.\n\n"
        f"Happy learning!\n"
        f"— EduCore Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=[enrollment.student.email],
            fail_silently=False,
        )
        logger.info("Enrollment notification sent to %s", enrollment.student.email)
    except Exception as exc:
        logger.error("Failed to send enrollment email: %s", exc)
        raise self.retry(exc=exc, countdown=60)
