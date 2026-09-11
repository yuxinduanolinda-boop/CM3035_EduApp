from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
)
from .serializers import UserSerializer


@extend_schema(
    summary='Search users',
    description=(
        'Search active EduApp users by username, '
        'first name, last name, or profile full name. '
        'Only authenticated teachers can use this endpoint.'
    ),
    parameters=[
        OpenApiParameter(
            name='q',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                'Optional search text used to match '
                'username, first name, last name, '
                'or profile full name.'
            ),
            examples=[
                OpenApiExample(
                    'Student search',
                    value='student',
                    summary='Search for a student'
                ),
                OpenApiExample(
                    'Name search',
                    value='Hao',
                    summary='Search by name'
                ),
            ],
        ),
    ],
    responses={
        200: UserSerializer(many=True),
        403: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Successful response',
            response_only=True,
            value=[
                {
                    'username': 'student1',
                    'email': 'student@example.com',
                    'full_name': 'Student One',
                    'role': 'student',
                }
            ],
        ),
        OpenApiExample(
            'Forbidden response',
            response_only=True,
            value={
                'detail': 'Only teachers can search users.'
            },
            status_codes=['403'],
        ),
    ],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list_api(request):
    """
    Return users matching the search query.

    GET parameters:
        q: Optional search text used to match username,
        first name, last name or profile full name.

    Only authenticated teachers can access this endpoint.

    Returns:
        A JSON list containing username, email, full name and role.
    """
    if not hasattr(request.user, 'profile'):
        return Response(
            {'detail': 'User profile not found.'},
            status=403
        )

    if request.user.profile.role != 'teacher':
        return Response(
            {'detail': 'Only teachers can search users.'},
            status=403
        )

    search_query = request.GET.get('q', '').strip()

    users = User.objects.filter(
        is_active=True,
        profile__isnull=False
    ).select_related('profile')

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(profile__full_name__icontains=search_query)
        )

    users = users.order_by('username')

    serializer = UserSerializer(users, many=True)

    return Response(serializer.data)