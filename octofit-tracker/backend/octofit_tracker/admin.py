from django.contrib import admin
from .models import User, Team, Activity, Workout, Leaderboard


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'team', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_filter = ['team', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'bio', 'profile_image')
        }),
        ('Team', {
            'fields': ('team',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'duration', 'activity_date']
    search_fields = ['user__username', 'type']
    list_filter = ['type', 'activity_date', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Activity Information', {
            'fields': ('user', 'type', 'duration', 'activity_date')
        }),
        ('Details', {
            'fields': ('distance', 'calories_burned', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['name', 'difficulty', 'duration', 'created_at']
    search_fields = ['name', 'description', 'exercises']
    list_filter = ['difficulty', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Workout Information', {
            'fields': ('name', 'description', 'difficulty')
        }),
        ('Details', {
            'fields': ('duration', 'exercises', 'target_muscle_groups')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'rank', 'score', 'total_activities', 'total_duration']
    search_fields = ['user__username']
    list_filter = ['rank', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'rank']
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Scores and Rankings', {
            'fields': ('score', 'rank', 'team_score')
        }),
        ('Statistics', {
            'fields': ('total_activities', 'total_duration')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-score']
