from django import forms
from courses.models import Course

#use this form for students to enroll on courses
#Hiddeninput is used to hide this from. This form is used in the CourseDetailView to display the button to enroll
class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(queryset = Course.objects.all(),
                                    widget = forms.HiddenInput)