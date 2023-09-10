from django.urls import path 
from . import views 


urlpatterns = [
    #url patterns for the list, create,edit and delete course views.
    path('mine/', views.ManageCourseListView.as_view(), name = 'manage_course_list'),
    path('create/', views.CourseCreateView.as_view(), name = 'course_create'),
    path('<pk>/edit/', views.CourseUpdateView.as_view(), name = 'course_edit'),
    path('<pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),
    path('<pk>/module/', views.CourseModuleUpdateView.as_view(), name='course_module_update'),
    #To create new text, video, image, or file objects and add them to a  module.
    #It includes the module_id and model_name parameters. The first one allows linking the
    # new content object to the given module. The latter specifies the content model to build the form for
    path('module/<int:module_id>/content/<model_name>/create/', views.ContentCreateUpdateView.as_view(), name='module_content_create'),
    #To update an existing text, video, image, or file object. It includes the module_id and model_name parameters and an id parameter
    #  to identify the content that is being updated.
    path('module/<int:module_id>/content/<model_name>/<id>/', views.ContentCreateUpdateView.as_view(), name='module_content_update'),
    path('content/<int:id>/delete/', views.ContentDeleteView.as_view(), name='module_content_delete'),
    path('module/<int:module_id>', views.ModuleContentListView.as_view(), name='module_content_list'),

]