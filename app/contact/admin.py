from django.contrib import admin

from .models import Contact


@admin.register(Contact)
class FallenBirdAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "phone",
        "email",
        "address",
        "comment",
    ]
    list_filter = ("name", "phone", "email", "address", "comment")
