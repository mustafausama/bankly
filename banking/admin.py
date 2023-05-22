from django.contrib import admin
from .models import *
from django.core.exceptions import ValidationError
from django.contrib import messages


class AdminValidationError(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        try:
            obj.save()  # Call the original save method
        except ValidationError as e:
            messages.set_level(request, messages.ERROR)
            self.message_user(request, e.message, level=messages.ERROR)


# Register your models here.
admin.site.register(Account, AdminValidationError)
admin.site.register(Transaction, AdminValidationError)
admin.site.register(Notification, AdminValidationError)
