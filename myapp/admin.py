from django.contrib import admin

from myapp.models import Task


# Register your models here.
class TodoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'description', 'done')
    list_display_links = ('id', 'user', 'title')
    search_fields = ('id', 'user', 'title', 'description')
    list_editable = ('done',)
    list_filter = ('done',)


admin.site.register(Task, TodoAdmin)
