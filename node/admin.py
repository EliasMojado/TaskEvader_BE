from django.contrib import admin
from .models import Node

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display   = ('id', 'icon', 'title', 'parent', 'priority', 'status', 'deadline')
    list_filter    = ('status', 'priority', 'deadline')
    search_fields  = ('title', 'description')
    raw_id_fields  = ('parent', 'collaborators')
    filter_horizontal = ('collaborators',)
