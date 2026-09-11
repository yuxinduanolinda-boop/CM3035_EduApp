from celery import shared_task

from django.contrib.auth.models import User

from .models import Notification


@shared_task
def create_enrolment_notification(
    teacher_id,
    student_name,
    course_title
):
    """Create a notification when a student enrols."""
    teacher = User.objects.get(pk=teacher_id)

    Notification.objects.create(
        user=teacher,
        message=(
            f'{student_name} enrolled in '
            f'{course_title}.'
        )
    )


@shared_task
def create_material_notifications(
    student_ids,
    material_title,
    course_title
):
    """Notify enrolled students about new course material."""
    students = User.objects.filter(
        id__in=student_ids
    )

    for student in students:
        Notification.objects.create(
            user=student,
            message=(
                f'New material "{material_title}" was added to '
                f'{course_title}.'
            )
        )