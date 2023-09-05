#CREATE CUSTOM ORDER FIELD 

#it inherits from the PositiveIntegerField field provided by Django
# the field overrides the pre_save() method of the PositiveIntegerField.
#It has two functionalities: 
# 1. automatically assign an order value when no specific order is provided
# 2. order objects with respect to other fields - cousrse modules will be ordered with respect to course they belong to
# and module contents with respect to module they belong to 
#https://docs.djangoproject.com/en/4.2/ref/signals/
#https://docs.djangoproject.com/en/4.2/howto/custom-model-fields/

from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveBigIntegerField):
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields 
        super().__init__(*args, **kwargs)


    #the method overrides the PosetiveIntegerField which is executed above
    def pre_save(self, model_instance, add):        
        #Check whether a value already exists for this field in the model instance.
        #self.attname is attribute name given to the field.
        #if the attribute's value is not None, it calculates the order you should give it
        if getattr(model_instance, self.attname) is None:
            #filter by objects with the same field values for the fields in 'for_fields
            try:
                #build a queryset and retrive all objects for the fields's model
                qs = self.model.objects.all()
                #if there is any field names in the for_fields attribute of the field, filter the queryset by the current value 
                #of the model fields in for_fields.
                if self.for_fields:

                    query = {field:getattr(model_instance, field)\
                             for field in self.for_fields}
                    qs = qs.filter(**query)

                #get the order of the highest or last item in order from the database
                #if no object is found, it assumes this object is the first one and assign order 0 to it
                last_item = qs.latest(self.attname)
                #if an object is found, add 1 to the highest order found
                value  = last_item.order + 1
            except ObjectDoesNotExist:
                value = 0

            #assign the calculated order to the field's value in the odel instance and return it
            setattr(model_instance, self.attname, value)
            return value
        else:
            #if the model instance has value for the current field, use it instead of calculating it
            return super().pre_save(model_instance, add)

