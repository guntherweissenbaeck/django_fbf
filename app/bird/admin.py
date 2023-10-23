from django.contrib import admin

from .models import Bird, FallenBird, BirdStatus, Circumstance, Image


@admin.register(FallenBird)
class FallenBirdAdmin(admin.ModelAdmin):
    list_display = [
        "bird",
        "age",
        "sex",
        "date_found",
        "place",
        "created",
        "updated",
        "user",
        "status",
    ]
    list_filter = ("bird", "created", "user", "status")


@admin.register(Bird)
class BirdAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(BirdStatus)
class BirdStatusAdmin(admin.ModelAdmin):
    list_display = ["id", "description"]


@admin.register(Circumstance)
class CircumstanceAdmin(admin.ModelAdmin):
    list_display = ["description"]


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ["id", "image"]
