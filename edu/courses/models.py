from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .fields import OrderField

class Subject(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return self.title
    
class Course(models.Model):
    #instructor who created this course
    owner = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(User, related_name='course_joined', blank=True)

    class Meta:
        ordering = ['created']
        

    def __str__(self) -> str:
        return self. title

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models. CharField(max_length=100)
    description = models.TextField(blank=True)
    #the order for the new module will be assigned by adding 1 to the last module of the same Course object
    order = OrderField(blank = True, for_fields=['course'])


    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return f'{self.order}.{self.title}'
    
   
    
class Content(models.Model):
    
    #note: Assigning a normal ForeignKey an only point to one other model. So we use GenericForeignKey to work around this and this allows the relationship to be with any model
    #Unlike for the ForeignKey, a database index is not automatically created on the GenericForeignKey, so it’s recommended that you use Meta.indexes to add your own multiple column index.
    #More details https://docs.djangoproject.com/en/4.2/ref/contrib/contenttypes/
    #
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    #model__in field lookup to filter the query to the ContentType objects with
    # a model attribute that is 'text', 'video', 'image', or 'file'.
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE,
                                     limit_choices_to={'model_in':(
                                         'text',
                                         'video',
                                         'image',
                                         'file' )})
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type','object_id')
    order = OrderField(blank = True, for_fields=['module'])

    def __str__(self):
        return self.module

    class Meta:
        ordering = ['order']
        # indexes = [
        #     models.Index(fields=["content_type", "object_id"]),
        # ]
        

#create an abstract base class model, Meta inheritance 
#Different model for each type of content is used. Content models will have some common fields, but they differ in the actual data they can store.
#This allows to create a single interface for different types of content.    
#Define an abstract model called ItemBase. Django doesn't create any database tables for abstract model.
#A database table is created for each child model
class ItemBase(models.Model):
    #owner field allows you to store which user created the content. So we need a different related_name for each sub-model.
    # Django allows to specify a placeholder for the model class name related_name attribute as %(class)s. the reverse relationship for child models will be text_related,
    #file_related,image_related and video_related
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        
    def __str__(self) -> str:
        return self. title
    

class Text(ItemBase):
    content = models.TextField()

class File(ItemBase):
    file = models.FileField(upload_to='files')

class Image(ItemBase):
    file = models.FileField(upload_to='images')

class Video(ItemBase):
    url = models.URLField()

