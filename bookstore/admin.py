from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'uploaded_by', 'category')
    search_fields = ('title', 'author', 'uploaded_by', 'category__name')
    list_filter = ('category',)
admin.site.register(User)
admin.site.register(DeleteRequest)
admin.site.register(Feedback)
