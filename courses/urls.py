from django.urls import path

from .views import (
    CourseCreateView,
    CourseDetailView,
    CourseListView,
    block_student,
    course_students,
    enrol_course,
    remove_student,
    upload_material,
    leave_feedback,
)
urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path(
        '<int:pk>/',
        CourseDetailView.as_view(),
        name='course_detail'
    ),
    path(
        '<int:pk>/enrol/',
        enrol_course,
        name='enrol_course'
    ),
    path(
        '<int:pk>/students/',
        course_students,
        name='course_students'
    ),
    path(
        '<int:course_pk>/students/<int:student_pk>/remove/',
        remove_student,
        name='remove_student'
    ),
    path(
        '<int:course_pk>/students/<int:student_pk>/block/',
        block_student,
        name='block_student'
    ),
    path(
        '<int:pk>/materials/upload/',
        upload_material,
        name='upload_material'
    ),
    path(
        '<int:pk>/feedback/',
        leave_feedback,
        name='leave_feedback'
    ),
]