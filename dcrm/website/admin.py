from django.contrib import admin
from .models import Record
from .models import Property
from .models import User

# Register your models here

admin.site.register(Record)
admin.site.register(Property)
admin.site.register(User)