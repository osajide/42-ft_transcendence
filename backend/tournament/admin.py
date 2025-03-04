from django.contrib import admin
from .models import *

# Register your models here.


for model in [Tournament, Tournament_Particapent]:
	admin.site.register(model)