from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.User)
admin.site.register(models.Token)
admin.site.register(models.RegistrationUserData)
admin.site.register(models.RecoverUserPasswordData)
