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
            return apps.get_model(app_label='courses', model_name=model_name)
        return None
    
    # Generate a dynamic form using modelform_factory().
    # Exclude common fields such as 'owner', 'order', 'created', and 'updated' from the form.
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)
    
    # The dispatch() method handles URL parameters and stores the corresponding module, model, and content object as class attributes:
    # module_id: ID of the associated module.
    # model_name: Model name for the content to create/update.
    # id: ID of the object being updated (None for new objects).
    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module, id=module_id, course_owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, module_id, model_name, id)
    
    #get(): Executed when a GET request is received. Build the model form for the Text, Video,
    # Image, or File instance that is being updated. Otherwise, pass no instance to create a new
    # object, since self.obj is None if no ID is provided.    
    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance = self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})
    
    #post(): Executed when a POST request is received. Build the model form, passing any
    # submitted data and files to it. Then validate it. If the form is valid, create a new object
    # and assign request.user as its owner before saving it to the database. Check for the id
    # parameter. If no ID is provided, then the user is creating a new object instead of updating
    # an existing one. If this is a new object, create a Content object for the given module and associate the new content with it.
    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance = self.obj, data = request.POST, files = request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()

            if not id:
                Content.objects.create(module = self.module, item=obj)
                return redirect('module_content_list', self.module.id)
            return self.render_to_response({'form':form, 'object':self.obj})