from django.contrib import admin

from .models import Bird, FallenBird, BirdStatus


@admin.register(FallenBird)
class FallenBirdAdmin(admin.ModelAdmin):
    list_display = [
        "bird",
        "date_found",
        "place",
        "created",
        "updated",
        "user"]
    list_filter = ("bird", "created", "user")


@admin.register(Bird)
class BirdAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(BirdStatus)
class BirdStatusAdmin(admin.ModelAdmin):
    list_display = ["description"]
