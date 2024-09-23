from django.contrib import admin

from .models import Object, Voting, VotingObject


@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'address')
    search_fields = ('name', 'address')
    list_filter = ('status',)
    ordering = ('name',)


@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at',
                    'formed_at', 'completed_at',
                    'voting_date', 'user', 'moderator')
    list_filter = ('status', 'voting_date')
    search_fields = ('title',)
    ordering = ('created_at',)
    date_hierarchy = 'voting_date'


@admin.register(VotingObject)
class VotingObjectAdmin(admin.ModelAdmin):
    list_display = ('voting', 'object', 'votes_count')
    list_filter = ('voting',)
    search_fields = ('voting__title', 'object__name')
    ordering = ('voting',)
