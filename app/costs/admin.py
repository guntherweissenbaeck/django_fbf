from django.contrib import admin

from .models import Costs

@admin.register(Costs)
class FallenBirdAdmin(admin.ModelAdmin):
    list_display = [
        "id_bird",
        "costs",
        "created",
        "comment",
        "user",
        ]
    list_filter = ("id_bird", "created")
