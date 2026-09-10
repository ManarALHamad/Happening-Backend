
#when I logIn into Django admin I will be able to manage all the important happening data

from django.contrib import admin

from .models import (
    Profile,
    Startup,
    StartUpRole,
    Application,
    TeamMember,
)

@admin.register(Profile)

class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "user_type",
        "experience_level",
        "location",
        "created_at",
    ]

    list_filter = [
        "user_type",
        "experience_level",
    ]

    search_fields = [
        "user__username",
        "user__email",
    ]

@admin.register(Startup)
class StartupAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "founder",
        "industry",
        "stage",
        "is_recruiting",
        "created_at",
    ]

    list_filter = [
        "industry",
        "stage",
        "is_recruiting",
    ]

    search_fields = [
        "name",
        "founder__username",
    ]

@admin.register(StartUpRole)
class StartUpRoleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "startup",
        "role_type",
        "is_open",
        "created_at",
    ]

    list_filter = [
        "role_type",
        "is_open",
    ]

    search_fields = [
        "title",
        "startup__name",
    ]

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "applicant",
        "role",
        "status",
        "created_at",
    ]

    list_filter = [
        "status",
    ]

    search_fields = [
        "applicant__username",
        "role__title",
        "role__startup__name",
    ]

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "startup",
        "role",
        "joined_at",
    ]

    search_fields = [
        "user__username",
        "startup__name",
        "role",
    ]