from django.contrib import admin

from .models import Bird, FallenBird, BirdStatus, Circumstance


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
    list_display = ["name", "melden_an_naturschutzbehoerde", "melden_an_jagdbehoerde", "melden_an_wildvogelhilfe_team"]
    list_filter = ["melden_an_naturschutzbehoerde", "melden_an_jagdbehoerde", "melden_an_wildvogelhilfe_team"]
    fields = ('name', 'description', 'melden_an_naturschutzbehoerde', 'melden_an_jagdbehoerde', 'melden_an_wildvogelhilfe_team')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by when creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BirdStatus)
class BirdStatusAdmin(admin.ModelAdmin):
    list_display = ["id", "description"]


@admin.register(Circumstance)
class CircumstanceAdmin(admin.ModelAdmin):
    list_display = ["description"]
