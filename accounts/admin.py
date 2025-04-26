from django.contrib import admin
from django.utils.html import format_html

from .models import User as ClientUser

@admin.register(ClientUser)
class ClientUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'name',
        'profile_pic_preview',
    )
    readonly_fields = ('profile_pic_preview',)
    search_fields = ('username', 'name')
    ordering = ('id',)

    def profile_pic_preview(self, obj):
        if obj.profile_pic:
            return format_html(
                '<img src="{}" '
                'style="width:50px; height:50px; object-fit:cover; '
                'border-radius:5px; border:1px solid #ccc;" />',
                obj.profile_pic.url
            )
        return "–"
    profile_pic_preview.short_description = 'Profile Picture'
