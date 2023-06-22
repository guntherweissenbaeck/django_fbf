from django.contrib import admin

from .models import Bird, FallenBird


@admin.register(FallenBird)
class ContractAdmin(admin.ModelAdmin):
    list_display = [
        "bird",
        "date_found",
        "place",
        "created",
        "updated",
        "user"]
    list_filter = ("bird", "created", "user")


@admin.register(Bird)
class ContractAdmin(admin.ModelAdmin):
    list_display = ["name"]
