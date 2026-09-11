from django import forms

from .models import Course, CourseFeedback, CourseMaterial


class CourseForm(forms.ModelForm):
    """Form used by teachers to create courses."""

    class Meta:
        model = Course
        fields = ('title', 'description')


class CourseMaterialForm(forms.ModelForm):
    """Form used by teachers to upload course materials."""

    class Meta:
        model = CourseMaterial
        fields = ('title', 'file')


class CourseFeedbackForm(forms.ModelForm):
    """Form used by students to leave course feedback."""

    class Meta:
        model = CourseFeedback
        fields = ('rating', 'comment')
        widgets = {
            'rating': forms.NumberInput(
                attrs={
                    'min': 1,
                    'max': 5,
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'rows': 4,
                }
            ),
        }