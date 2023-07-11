from django.contrib import admin

from .models import Aviary


@admin.register(Aviary)
class AviaryAdmin(admin.ModelAdmin):
    list_display = [
        "description",
        "condition",
        "last_ward_round",
        ]
    list_filter = ("description", "condition", "last_ward_round")
