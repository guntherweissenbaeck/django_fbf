from django.contrib import admin

from django.contrib import admin
from .models import Rescuer


@admin.register(Rescuer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        "last_name",
        "first_name",
        "street",
        "street_number",
        "city",
        "email",
        "phone",
        "user",
    ]
