from django.contrib import admin
from .models import *

# Register your models here.

for model in [Conversation, Message]:
	admin.site.register(model)