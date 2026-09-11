from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView

from .forms import CourseForm, CourseMaterialForm, CourseFeedbackForm
from .models import Course, CourseBlock, CourseFeedback, Enrollment
#from notifications.models import Notification
from notifications.tasks import create_enrolment_notification, create_material_notifications


class CourseListView(LoginRequiredMixin, ListView):
    """Display all available courses."""

    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'


class CourseDetailView(LoginRequiredMixin, DetailView):
    """Display details for one course."""

    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    def get_context_data(self, **kwargs):
        """Add enrolment and feedback status for the current student."""
        context = super().get_context_data(**kwargs)

        if self.request.user.profile.role == 'student':
            context['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user,
                course=self.object
            ).exists()

            context['has_feedback'] = CourseFeedback.objects.filter(
                student=self.request.user,
                course=self.object
            ).exists()
        else:
            context['is_enrolled'] = False
            context['has_feedback'] = False

        return context


class CourseCreateView(LoginRequiredMixin, CreateView):
    """Allow teachers to create a new course."""

    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def dispatch(self, request, *args, **kwargs):
        """Restrict course creation to teachers."""
        if request.user.profile.role != 'teacher':
            return HttpResponseForbidden(
                'Only teachers can create courses.'
            )

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Set the logged-in teacher as the course owner."""
        form.instance.teacher = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the newly created course."""
        return f'/courses/{self.object.pk}/'

def enrol_course(request, pk):
    """Allow a student to enrol on a course."""
    if request.method != 'POST':
        return HttpResponseForbidden(
            'Course enrolment must use POST.'
        )

    if request.user.profile.role != 'student':
        return HttpResponseForbidden(
            'Only students can enrol on courses.'
        )

    course = get_object_or_404(Course, pk=pk)
    blocked = CourseBlock.objects.filter(
        teacher=course.teacher,
        student=request.user,
        course=course
    ).exists()

    if blocked:
        return HttpResponseForbidden(
            'You are blocked from this course.'
        )   

    already_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).exists()

    if not already_enrolled:
        Enrollment.objects.create(
            student=request.user,
            course=course
        )

        create_enrolment_notification.delay(
            teacher_id=course.teacher.id,
            student_name=request.user.profile.full_name,
            course_title=course.title
        )

    return redirect('course_detail', pk=course.pk)

def course_students(request, pk):
    """Display enrolled students to the course teacher."""
    if not request.user.is_authenticated:
        return redirect('login')

    course = get_object_or_404(Course, pk=pk)

    if (
        request.user.profile.role != 'teacher'
        or course.teacher != request.user
    ):
        return HttpResponseForbidden(
            'Only the course teacher can view enrolled students.'
        )

    enrollments = Enrollment.objects.filter(
        course=course
    ).select_related('student', 'student__profile')

    return render(
        request,
        'courses/course_students.html',
        {
            'course': course,
            'enrollments': enrollments,
        }
    )

def remove_student(request, course_pk, student_pk):
    """Remove a student from a teacher's course."""
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return HttpResponseForbidden(
            'Student removal must use POST.'
        )

    course = get_object_or_404(
        Course,
        pk=course_pk,
        teacher=request.user
    )

    enrollment = get_object_or_404(
        Enrollment,
        course=course,
        student_id=student_pk
    )

    enrollment.delete()

    return redirect(
        'course_students',
        pk=course.pk
    )

def block_student(request, course_pk, student_pk):
    """Block a student from a teacher's course."""
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return HttpResponseForbidden(
            'Student blocking must use POST.'
        )

    course = get_object_or_404(
        Course,
        pk=course_pk,
        teacher=request.user
    )

    student = get_object_or_404(
        User,
        pk=student_pk
    )

    CourseBlock.objects.get_or_create(
        teacher=request.user,
        student=student,
        course=course
    )

    Enrollment.objects.filter(
        course=course,
        student=student
    ).delete()

    return redirect(
        'course_students',
        pk=course.pk
    )

def upload_material(request, pk):
    """Allow the course teacher to upload teaching material."""
    if not request.user.is_authenticated:
        return redirect('login')

    course = get_object_or_404(
        Course,
        pk=pk,
        teacher=request.user
    )

    if request.method == 'POST':
        form = CourseMaterialForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()

            enrolled_student_ids = list(
                Enrollment.objects.filter(
                    course=course
                ).values_list(
                    'student_id',
                    flat=True
                )
            )

            create_material_notifications.delay(
                student_ids=enrolled_student_ids,
                material_title=material.title,
                course_title=course.title
            )

            return redirect(
                'course_detail',
                pk=course.pk
            )

    else:
        form = CourseMaterialForm()

    return render(
        request,
        'courses/material_form.html',
        {
            'form': form,
            'course': course,
        }
    )

def leave_feedback(request, pk):
    """Allow an enrolled student to leave feedback."""
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.profile.role != 'student':
        return HttpResponseForbidden(
            'Only students can leave course feedback.'
        )

    course = get_object_or_404(Course, pk=pk)

    is_enrolled = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).exists()

    if not is_enrolled:
        return HttpResponseForbidden(
            'You must be enrolled in this course to leave feedback.'
        )

    if request.method == 'POST':
        form = CourseFeedbackForm(request.POST)

        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = request.user
            feedback.course = course
            feedback.save()

            return redirect(
                'course_detail',
                pk=course.pk
            )

    else:
        form = CourseFeedbackForm()

    return render(
        request,
        'courses/feedback_form.html',
        {
            'form': form,
            'course': course,
        }
    )