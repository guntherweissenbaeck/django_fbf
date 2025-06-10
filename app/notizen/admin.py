from django.contrib import admin
from .models import Notiz, Page


@admin.register(Notiz)
class NotizAdmin(admin.ModelAdmin):
    list_display = ['name', 'erstellt_von', 'erstellt_am', 'geaendert_am', 'attached_to_model_name', 'attached_to_object_str']
    list_filter = ['erstellt_am', 'geaendert_am', 'content_type']
    search_fields = ['name', 'inhalt']
    readonly_fields = ['erstellt_am', 'geaendert_am']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.erstellt_von = request.user
        super().save_model(request, obj, form, change)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ['name', 'identifier', 'description']
    search_fields = ['name', 'identifier', 'description']
    readonly_fields = ['identifier']
