from django.contrib import admin

from .models import (
    Course,
    CourseBlock,
    CourseFeedback,
    CourseMaterial,
    Enrollment,
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('teacher',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course',)

@admin.register(CourseBlock)
class CourseBlockAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'course',
        'teacher',
        'blocked_at'
    )
    list_filter = ('course',)

@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_at')
    list_filter = ('course',)


@admin.register(CourseFeedback)
class CourseFeedbackAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'rating', 'created_at')
    list_filter = ('rating', 'course')