from django.contrib import admin

from .models import Questionnaire, User

admin.site.register(User)
admin.site.register(Questionnaire)
