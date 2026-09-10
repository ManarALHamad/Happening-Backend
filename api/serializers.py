#Convert model instances into simple data that DRF can send as JSON.

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import (
    Profile,
    Startup,
    StartUpRole,
    Application,
    TeamMember,
)

#user serializer

class UserSerializer(serializers.ModelSerializer):

    _id = serializers.CharField(source="pk", read_only=True)

    class Meta:

        model = User
        fields = [
            "_id",
            "username",
            "email",
        ]

#profile serializer

class ProfileSerializer(serializers.ModelSerializer):
     _id = serializers.CharField(source="pk", read_only=True)
     user = UserSerializer(read_only=True)

     createdAt = serializers.DateTimeField(
        source="created_at",
        read_only=True
    )

class Meta:
      model = Profile
      fields = [
         "_id",
         "user",
         "user_type",
         "bio",
         "location",
         "skills",
         "experience_level",
         "linkedin_url",
         "github_url",
         "portfolio_url",
         "profile_image",
         "createdAt",
        ]

# StartUp role serializer 

class StartUpRoleSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source="pk", read_only=True)

    createdAt = serializers.DateTimeField(
        source="created_at",
        read_only=True
    )

    class Meta:
        model = StartUpRole
        fields = [
            "_id",
            "title",
            "role_type",
            "description",
            "required_skills",
            "is_open",
            "createdAt",
        ]

# TeamMember serializer

class TeamMemberSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source="pk", read_only=True)
    user = UserSerializer(read_only=True)

    joinedAt = serializers.DateTimeField(
        source="joined_at",
        read_only=True
    )

    class Meta:
        model = TeamMember
        fields = [
            "_id",
            "user",
            "role",
            "joinedAt",
        ]

# StartUp Serializer

class StartupSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(source="pk", read_only=True)

    founder = UserSerializer(read_only=True)

    roles = StartUpRoleSerializer(
        many=True,
        read_only=True
    )

    team_members = TeamMemberSerializer(
        many=True,
        read_only=True
    )

    createdAt = serializers.DateTimeField(
        source="created_at",
        read_only=True
    )

    updateAt = serializers.DateTimeField(
        source="updated_at",
        read_only=True
    )

    class Meta:
        model = Startup
        fields = [
            "_id",
            "name",
            "founder",
            "description",
            "problem",
            "solution",
            "industry",
            "stage",
            "location",
            "website",
            "logo",
            "is_recruiting",
            "roles",
            "team_members",
            "createdAt",
            "updatedAt",
        ]


# Application serializers

class ApplicationSerializer(serializers.ModelSerializer):

    _id = serializers.CharField(source="pk", read_only=True)

    applicant = UserSerializer(read_only=True)

    role = StartUpRoleSerializer(read_only=True)

    createdAt = serializers.DateTimeField(
        source="created_at",
        read_only=True
    )

    class Meta:
        model = Application
        fields = [
            "_id",
            "applicant",
            "role",
            "message",
            "status",
            "createdAt",
        ]

