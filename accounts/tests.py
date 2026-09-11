from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import UserProfile


class UserListAPITest(APITestCase):
    """Test the REST API used for teacher user search."""

    def setUp(self):
        """Create users and profiles used by the API tests."""
        self.teacher = User.objects.create_user(
            username='api_teacher',
            password='testpassword123',
            email='teacher@example.com'
        )
        UserProfile.objects.create(
            user=self.teacher,
            role='teacher',
            full_name='API Teacher'
        )

        self.student = User.objects.create_user(
            username='api_student',
            password='testpassword123',
            email='student@example.com'
        )
        UserProfile.objects.create(
            user=self.student,
            role='student',
            full_name='API Student'
        )

        self.other_student = User.objects.create_user(
            username='another_student',
            password='testpassword123',
            email='other@example.com'
        )
        UserProfile.objects.create(
            user=self.other_student,
            role='student',
            full_name='Another Student'
        )

        self.url = reverse('user_list_api')

    def test_teacher_can_access_user_api(self):
        """A logged-in teacher should receive a list of users."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_student_cannot_access_user_api(self):
        """Students should not be allowed to search users."""
        self.client.force_authenticate(user=self.student)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_query_filters_users(self):
        """The search query should return only matching users."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(
            self.url,
            {'q': 'another'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['username'],
            'another_student'
        )

    def test_anonymous_user_cannot_access_user_api(self):
        """Unauthenticated users should not access the API."""
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_api_returns_expected_user_fields(self):
        """The API should return the expected serializer fields."""
        self.client.force_authenticate(user=self.teacher)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_user = response.data[0]

        self.assertIn('username', first_user)
        self.assertIn('email', first_user)
        self.assertIn('full_name', first_user)
        self.assertIn('role', first_user)
        
    def test_swagger_page_loads(self):
        """The Swagger UI page should load."""
        response = self.client.get(
            reverse('swagger_ui')
        )

        self.assertEqual(
            response.status_code,
            200
        )


    def test_schema_loads(self):
        """The OpenAPI schema should load."""
        response = self.client.get(
            reverse('api_schema')
        )

        self.assertEqual(
            response.status_code,
            200
        )