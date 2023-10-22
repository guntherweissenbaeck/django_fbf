from django.contrib import admin

from .models import Contact, ContactTag


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


@admin.register(ContactTag)
class ContactTagAdmin(admin.ModelAdmin):
    list_display = [
        "tag",
    ]
    list_filter = ("tag",)
