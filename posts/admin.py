from django.contrib import admin
from .models import Post, Group, Comment, Follow, PostRate


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title",)
    list_filter = ("slug",)
    empty_value_display = "-пусто-"


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "created", "author")
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author")
    empty_value_display = "-пусто-"


class PostRateAdmin(admin.ModelAdmin):
    list_display = ("pk", "post_id", "post", "user", "rate")
    empty_value_display = "-пусто-"

admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(PostRate, PostRateAdmin)
