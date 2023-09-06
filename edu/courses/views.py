from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Course
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy



class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner = self.request.user)

# Implments the form_valid() method, which is used by views that use Django's ModelFormixin mixin    
class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user #current user
        return super().form_valid(form)
    
class OwnerCourseMixin(OwnerMixin):
    model = Course #used for QuerySets. its used by all views
    fields = ['subject', 'title','slug','overview'] # the fields fo the model to build the model form of the CreateView and UpdateView views 
    success_url = reverse_lazy('manage_course_list') #redirects the user after the form is successfully submitted or object is deleted

#The templage_name attribute is used for CreateView and UpdateView views
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name= 'courses/manage/course/form.html'

#inherits from OwnerCourseMixin and ListView. The template listes course
class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'

#inherits from OwnerCourseMixin and and Createview. It uses the template defined in OwnerCourseMixin 
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    pass 

#inherits from OwnerCourseMixin and and Updateview. It uses the template defined in OwnerCourseMixin 
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    pass 

#inherits from OwnerCourseMixin and and Deleteview. It uses the template to confirm the course delition 
class CourseDeleteView(OwnerCourseEditMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'

