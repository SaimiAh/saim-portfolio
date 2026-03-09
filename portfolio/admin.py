from django.contrib import admin
from .models import BlogPost, ContactMessage


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'created_at')
    list_filter = ('published',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('published',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'read', 'created_at')
    list_filter = ('read',)
    search_fields = ('name', 'email', 'subject')
    list_editable = ('read',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
