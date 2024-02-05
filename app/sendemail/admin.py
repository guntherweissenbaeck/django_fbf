from django.contrib import admin

from .models import Emailadress, BirdEmail


@admin.register(Emailadress)
class EmailaddressAdmin(admin.ModelAdmin):
    list_display = ["email_address", "created_at", "updated_at", "user"]
    search_fields = ["email_address"]
    list_filter = ["created_at", "updated_at", "user"]
    list_per_page = 20


@admin.register(BirdEmail)
class BirdEmailAdmin(admin.ModelAdmin):
    list_display = ["bird", "email"]
    search_fields = ["bird", "email"]
    list_filter = ["bird", "email"]
    list_per_page = 20
