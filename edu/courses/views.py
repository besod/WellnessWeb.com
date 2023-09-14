from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Course,Module, Content,Subject
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from braces.views import CsrfExemptMixin,JsonRequestResponseMixin
from django.db.models import Count
from django.views.generic.detail import DetailView
from students.forms import CourseEnrollForm

class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

# Implments the form_valid() method, which is used by views that use Django's ModelFormixin mixin    
class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

# LoginRequiredMixin: replicates the login_required decorators functionality
#  PermissionRequiredMixin: grants access to the view to users with specific permission    
class OwnerCourseMixin(OwnerMixin,LoginRequiredMixin,PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')

#The templage_name attribute is used for CreateView and UpdateView views
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'

#inherits from OwnerCourseMixin and ListView. The template listes course
class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'

#inherits from OwnerCourseMixin and and Createview. It uses the template defined in OwnerCourseMixin 
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'

#inherits from OwnerCourseMixin and and Updateview. It uses the template defined in OwnerCourseMixin 
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'

#inherits from OwnerCourseMixin and and Deleteview. It uses the template to confirm the course delition 
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course' 
#inerits from Templateresponsemixin 
class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name='courses/course/list.html'
    def get(self, request, subject=None):
        
        subjects = Subject.objects.annotate(total_courses=Count('courses'))
        courses=Course.objects.annotate(total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            courses=courses.filter(subject=subject)
        return self.render_to_response({'subjects':subjects, 'subject':subject,'courses':courses})
    
class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    #this method is to include the enrollment form in the context for rendering the templates. 
    #it initializes the hidden course field for the form with current Course object so that it can be submitted directly
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course':self.object})

        return context
    
'''This module handles the formset to add, update, and delete modules for courses
It inherits from TemplateResponseMixin, which renders templates and returns HTTP response.
It requires template_name to be rendered and provides the method render_ro_response() to pass
it a context and render the template'''
class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    #get_formset method is used to create and return a formset for course modules. 
    # It takes optional data as a parameter, which can be used to populate the formset with user-submitted data
    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)
    
    #The dispatch method is responsible for handling the initial request and fetching the course object from the database.
    #  It uses get_object_or_404 to retrieve the course with the specified pk (primary key) while ensuring that the user making the request owns the course.
    def dispatch(self, request, pk):
        self.course=get_object_or_404(Course,id=pk,owner=request.user)
        return super().dispatch(request,pk)
    
    #Executed for GET requests
    #a formset is created using self.get_formset() and passed to the template along with the course object. 
    # This is used for rendering the initial form display.
    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset':formset})
    
    #Executed for POST requests.
    #It is used to handle form submissions.
    #  It creates a formset using the submitted data and checks if the formset is valid.
    #  If the formset is valid, it saves the changes and redirects the user to the course list view ('manage_course_list'). 
    # If the formset is not valid, it re-renders the template with error messages.
    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course, 'formset':formset})
    
''' This section handles creation and updating of various model's contents.'''
class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'
    # Check if the provided model_name is one of the valid content models: 'text', 'video', 'image', or 'file'.
    # Obtain the actual model class using Django's apps module.
    # Return None if the model_name is invalid.
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',
                                  model_name=model_name)
        return None
    # Generate a dynamic form using modelform_factory().
    # Exclude common fields such as 'owner', 'order', 'created', and 'updated' from the form.
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)
    # The dispatch() method handles URL parameters and stores the corresponding module, model, and content object as class attributes:
    # module_id: ID of the associated module.
    # model_name: Model name for the content to create/update.
    # id: ID of the object being updated (None for new objects).
    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,
                                       id=module_id,
                                       course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         owner=request.user)
        return super().dispatch(request, module_id, model_name, id)
    #get(): Executed when a GET request is received. Build the model form for the Text, Video,
    # Image, or File instance that is being updated. Otherwise, pass no instance to create a new
    # object, since self.obj is None if no ID is provided. 
    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})
    #post(): Executed when a POST request is received. Build the model form, passing any
    # submitted data and files to it. Then validate it. If the form is valid, create a new object
    # and assign request.user as its owner before saving it to the database. Check for the id
    # parameter. If no ID is provided, then the user is creating a new object instead of updating
    # an existing one. If this is a new object, create a Content object for the given module and associate the new content with it.
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,
                                        'object': self.obj})
    
class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,
                                     id=id,
                                     module_course_owner=request.user)
        module=content.module
        content.item.delet()
        content.delete()
        return redirect('module_content_list', module.id)

#This view gets the Module object with the given ID that belongs to the current user and renders a template with the given module 
class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(Module,
                                   id=module_id,
                                   course__owner=request.user)
        return self.render_to_response({'module': module})

'''Reordering Modules and their contents and using mixins from django-braces'''
#ModuleOrderView updates the order of the course modules.
#csrfexemptmixin: used to avoid checking the csrf token in POST requests. AJAX POST request is needed with out the need to pass a csrf_token
#Jsonrequestresponsemixin:parses the request data as json and serializes the response as json and returns http response with json content type
class ModuleOrderView(CsrfExemptMixin,JsonRequestResponseMixin,View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course_owner=request.user).update(order=order)
        return self.render_json_response({'saved':'OK'})
    
class ContentOrderView(CsrfExemptMixin,JsonRequestResponseMixin,View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module_course_owner=request.user.update(order=order))
        return self.render_json_response({'saved':'OK'})
