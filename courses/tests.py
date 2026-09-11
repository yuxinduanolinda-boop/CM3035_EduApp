from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import UserProfile

from .models import (
    Course,
    CourseBlock,
    CourseFeedback,
    CourseMaterial,
    Enrollment,
)


class CourseTestSetup(TestCase):
    """Create users and a course for course-related tests."""

    def setUp(self):
        self.teacher = User.objects.create_user(
            username='course_teacher',
            password='testpassword123'
        )
        UserProfile.objects.create(
            user=self.teacher,
            role='teacher',
            full_name='Course Teacher'
        )

        self.student = User.objects.create_user(
            username='course_student',
            password='testpassword123'
        )
        UserProfile.objects.create(
            user=self.student,
            role='student',
            full_name='Course Student'
        )

        self.other_teacher = User.objects.create_user(
            username='other_teacher',
            password='testpassword123'
        )
        UserProfile.objects.create(
            user=self.other_teacher,
            role='teacher',
            full_name='Other Teacher'
        )

        self.course = Course.objects.create(
            title='Test Course',
            description='Test course description',
            teacher=self.teacher
        )


class CourseModelTest(CourseTestSetup):
    """Test course-related database behaviour."""

    def test_course_is_created_with_teacher(self):
        self.assertEqual(self.course.teacher, self.teacher)
        self.assertEqual(self.course.title, 'Test Course')

    def test_enrollment_unique_per_student_and_course(self):
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        with self.assertRaises(Exception):
            Enrollment.objects.create(
                student=self.student,
                course=self.course
            )

    def test_feedback_unique_per_student_and_course(self):
        CourseFeedback.objects.create(
            student=self.student,
            course=self.course,
            rating=5,
            comment='Good course.'
        )

        with self.assertRaises(Exception):
            CourseFeedback.objects.create(
                student=self.student,
                course=self.course,
                rating=4,
                comment='Second feedback.'
            )


class CoursePermissionTest(CourseTestSetup):
    """Test teacher and student permissions."""

    def test_student_cannot_create_course(self):
        self.client.login(
            username='course_student',
            password='testpassword123'
        )

        response = self.client.get(
            reverse('course_create')
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_open_course_creation_page(self):
        self.client.login(
            username='course_teacher',
            password='testpassword123'
        )

        response = self.client.get(
            reverse('course_create')
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EnrollmentTest(CourseTestSetup):
    """Test student enrolment behaviour."""

    def test_student_can_enrol(self):
        self.client.login(
            username='course_student',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'enrol_course',
                args=[self.course.pk]
            )
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.assertTrue(
            Enrollment.objects.filter(
                student=self.student,
                course=self.course
            ).exists()
        )


    def test_student_cannot_enrol_when_blocked(self):
        CourseBlock.objects.create(
            teacher=self.teacher,
            student=self.student,
            course=self.course
        )

        self.client.login(
            username='course_student',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'enrol_course',
                args=[self.course.pk]
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertFalse(
            Enrollment.objects.filter(
                student=self.student,
                course=self.course
            ).exists()
        )


class CourseFeedbackTest(CourseTestSetup):
    """Test course feedback behaviour."""

    def test_enrolled_student_can_submit_feedback(self):
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        self.client.login(
            username='course_student',
            password='testpassword123'
        )

        response = self.client.post(
            reverse(
                'leave_feedback',
                args=[self.course.pk]
            ),
            {
                'rating': 5,
                'comment': 'Very good course.'
            }
        )

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        self.assertTrue(
            CourseFeedback.objects.filter(
                student=self.student,
                course=self.course
            ).exists()
        )


class CourseMaterialTest(CourseTestSetup):
    """Test teacher material uploads."""

    def test_teacher_can_upload_material(self):
        self.client.login(
            username='course_teacher',
            password='testpassword123'
        )

        test_file = SimpleUploadedFile(
            'test_material.txt',
            b'Test course material.',
            content_type='text/plain'
        )

        response = self.client.post(
            reverse(
                'upload_material',
                args=[self.course.pk]
            ),
            {
                'title': 'Week 1 Material',
                'file': test_file,
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_302_FOUND
        )

        self.assertTrue(
            CourseMaterial.objects.filter(
                course=self.course,
                title='Week 1 Material'
            ).exists()
        )

        test_file.close()