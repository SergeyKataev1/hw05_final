from django.contrib import admin

from .models import Group, Post, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'text', 'author', 'created')
    list_filter = ('created',)
    search_fields = ('text',)


admin.site.register(Comment, CommentAdmin)
admin.site.register(Group)
admin.site.register(Post, PostAdmin)