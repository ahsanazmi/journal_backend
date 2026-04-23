from django.contrib import admin
from .models import Manuscript, Review, Author


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0


@admin.register(Manuscript)
class ManuscriptAdmin(admin.ModelAdmin):
    list_display = ('paper_id', 'title', 'status', 'created_at')
    inlines = [ReviewInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('manuscript', 'reviewer', 'decision', 'assigned_at')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile')