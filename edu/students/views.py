from django.http import HttpResponse
from django.shortcuts import render

from django.urls import reverse_lazy
#CreateView provides functionality for creating model objects
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseEnrollForm
from django.views.generic.list import ListView
from courses.models import Course
from django.views.generic.detail import DetailView


class StudentRegistrationView(CreateView):
    #template path to render the view
    template_name = 'students/student/registration.html'
    #the form for creating objects which has ModelForm. Djangos UserCreationForm is the registration form to create User objects.
    form_class = UserCreationForm
    #redirect user when the form is successfully submitted.Reverse the url named student_course_list
    success_url = reverse_lazy('student_course_list')
    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data
        user = authenticate(username=cd['username'],
                            password=cd['password1'])
        login(self.request, user)
        return result

#this view inherits from LooginRequiredMixin mixin so  that only loggedin users can access the view. 
#it inherits from djangos FormView view
class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course =None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        return super().form_valid(form)
    
    #this method returns the url that the user will be redirected to
    def get_success_url(self):
        return reverse_lazy('student_course_detail', args=[self.course.id])
    
#the view to see courses that students are enrolled on. Loginqurieredmixin makes sure only loggedin users have access#
#listview for displaying list of course objects. 
#override the get_queryset to retrieve only the courses the student is enrolled on 
class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(DetailView):
    model = Course
    template_name = 'students/course/detail.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get course object
        course = self.get_object()
        if 'module_id' in self.kwargs:
            # get current module
            context['module'] = course.modules.get(id=self.kwargs['module_id'])
        else:
            # get first module
            context['module'] = course.modules.all()[0]
        return context