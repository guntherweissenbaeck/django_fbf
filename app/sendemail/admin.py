from django.contrib import admin

from .models import Emailadress


@admin.register(Emailadress)
class EmailaddressAdmin(admin.ModelAdmin):
    list_display = ["email_address", "is_naturschutzbehoerde", "is_jagdbehoerde", "is_wildvogelhilfe_team", "created_at", "updated_at", "user"]
    search_fields = ["email_address"]
    list_filter = ["is_naturschutzbehoerde", "is_jagdbehoerde", "is_wildvogelhilfe_team", "created_at", "updated_at", "user"]
    list_per_page = 20
    fieldsets = (
        (None, {
            'fields': ('email_address',)
        }),
        ('Notification Categories', {
            'fields': ('is_naturschutzbehoerde', 'is_jagdbehoerde', 'is_wildvogelhilfe_team'),
            'description': 'Select which types of notifications this email address should receive'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set user when creating new object
            obj.user = request.user
        super().save_model(request, obj, form, change)
