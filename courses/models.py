from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses_taught'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'],
                name='unique_student_course'
            )
        ]

    def __str__(self):
        return f'{self.student.username} - {self.course.title}'

class CourseBlock(models.Model):
    """Record when a teacher blocks a student from a course."""

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_blocks'
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_blocks'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='blocked_students'
    )
    blocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'student', 'course'],
                name='unique_course_block'
            )
        ]

    def __str__(self):
        return (
            f'{self.student.username} blocked from '
            f'{self.course.title}'
        )

class CourseMaterial(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='materials'
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='course_materials/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CourseFeedback(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='course_feedback'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    rating = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'course'],
                name='unique_student_course_feedback'
            )
        ]

    def __str__(self):
        return (
            f'{self.student.username} - '
            f'{self.course.title} - {self.rating}/5'
        )

