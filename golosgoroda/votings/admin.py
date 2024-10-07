from django.contrib import admin
from django.utils.html import format_html

from .models import Object, Voting, VotingObject


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'image_preview')
    list_filter = ('status',)
    search_fields = ('name', 'description')
    readonly_fields = ('image_preview',)
    fields = ('name', 'description', 'status', 'image', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />',
                               obj.image.url)
        return "-"
    image_preview.allow_tags = True
    image_preview.short_description = 'Превью изображения'


@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'formed_at', 'completed_at', 'voting_date', 'total_votes', 'user', 'moderator')
    list_filter = ('status', 'created_at', 'voting_date')
    search_fields = ('title', 'user__username', 'moderator__username')
    readonly_fields = ('total_votes',)
    date_hierarchy = 'created_at'
    actions = ['mark_as_completed', 'mark_as_rejected']

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} голосований завершено.')
    mark_as_completed.short_description = 'Завершить выбранные голосования'

    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} голосований отклонено.')
    mark_as_rejected.short_description = 'Отклонить выбранные голосования'


@admin.register(VotingObject)
class VotingObjectAdmin(admin.ModelAdmin):
    list_display = ('voting', 'object', 'votes_count')
    list_filter = ('voting__status', 'object__status')
    search_fields = ('voting__title', 'object__name')
    autocomplete_fields = ('voting', 'object')