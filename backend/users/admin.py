from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

# from reviews.models import (Review, Comment)

User = get_user_model()
admin.site.unregister(Group)


# class CommentInline(admin.StackedInline):
#     model = Comment
#     extra = 0


# class ReviewInline(admin.StackedInline):
#     model = Review
#     extra = 0


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """User information"""

    # inlines = (CommentInline, ReviewInline)
    list_display = ('pk', 'username', 'email', 'role',
                    'first_name', 'last_name')
    list_display_links = ('username', )
    search_fields = ['username']
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'

    # @admin.display(description="Комментарии")
    # def comments_count(self, obj):
    #     return obj.comments.all().count()

    # @admin.display(description="Отзывы")
    # def reviews_count(self, obj):
    #     return obj.reviews.all().count()
