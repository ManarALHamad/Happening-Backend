
# Views for the API(Application Programming Interface) Logic
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import (Profile, Startup, StartUpRole, Application, TeamMember)

from .serializers import (UserSerializer, ProfileSerializer, StartUpRoleSerializer, StartupSerializer, ApplicationSerializer, TeamMemberSerializer)


# create the jwt token 

def create_access_token(user):

    token = RefreshToken.for_user(user).access_token

    user_type = (
        user.profile.user_type
        if hasattr(user, "profile") #so if the user does not happening acc then its admin
        else "Admin"
    )
    
    token["payload"] = {
        "_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "user_type": user_type,

    }
    return str(token)

#SignUp post method 

@api_view(["POST"])
@permission_classes([AllowAny])
def sign_up(request):

    username = request.data.get("username", "").strip()
    email = request.data.get("email", "").strip()
    password = request.data.get("password", "")
    confirm_password = request.data.get("confirmPassword", "")
    user_type = request.data.get("user_type", "User")

    if not username or not email or not password:
        return Response(
            {"err": "Username, email and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if password != confirm_password:
        return Response(
            {"err": "Passwords do not match."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if user_type not in ("Founder", "User"):
        return Response(
            {"err":"Invalid user type"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if User.objects.filter(username=username).exists():
        return Response(
            {"err": "That username already taken"},
            status=status.HTTP_400_BAD_REQUEST,

        )
    if User.objects.filter(email=email).exists():
         return Response(
            {"err": "this email is already registered"},
            status=status.HTTP_400_BAD_REQUEST,
        
       )

    user = User.objects.create_user(

        username=username,
        email=email,
        password=password,
    )

    Profile.objects.create(
        user=user,
        user_type=user_type,
    )

    # access token creation

    token = create_access_token(user)

    return Response(
        {"token": token},
        status=status.HTTP_201_CREATED,
    )

# SignIn

@api_view(["POST"])
@permission_classes([AllowAny])
def sign_in(request):
    username = request.data.get("username", "").strip() #.strip() method removes extra spaces and hidden characters
    password = request.data.get("password", "")
    user = authenticate(
        username=username, 
        password=password
        )
    if user is None:
        return Response(
            {"err": "Invalid username or password."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    token = create_access_token(user)

    return Response({"token": token})

#users 

@api_view(["GET"])
def user_list(request):

    users = User.objects.all().order_by("username")
    
    serializer = UserSerializer(users, many=True)

    return Response(serializer.data)

#create and update the user or startup profile
#we used patch request that can update only one field without touching the other fields

@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def profile_detail(request):

    profile = request.user.profile

    #Get the profile

    if request.method == "GET":
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    #update the profile 

    if request.method in ["PUT", "PATCH"]:

        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

   
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

#image endpoint

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def profile_image_upload(request):

    profile = request.user.profile

    image = request.FILES.get("profile_image")

    if not image:
        return Response(
            {"err": "No image provided"},
            status=status.HTTP_400_BAD_REQUEST
        )

    profile.profile_image = image
    profile.save()

    serializer = ProfileSerializer(profile)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


#Create the startup get and post 

@api_view(["GET", "POST"])
def startup_list_create(request):

    # GET ALL STARTUPS
    if request.method == "GET":

        startups = Startup.objects.all()

        serializer = StartupSerializer(
            startups,
            many=True
        )

        return Response(serializer.data)

#here we create the startup

    if request.method == "POST":

        if request.user.profile.user_type != "Founder":
            return Response(
                {"err": "Only founders can create startups"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = StartupSerializer(
            data=request.data
        )
        if serializer.is_valid():

            serializer.save(
                founder=request.user #jwt re.user - founder
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

#startup logo 

@api_view(["POST"])
def startup_logo_upload(request, startup_id):

    startup = get_object_or_404(
        Startup,
        id=startup_id
    )

    # Only the founder who owns the startup can upload the logo
    if startup.founder != request.user:
        return Response(
            {"err": "Only the startup founder can upload the logo."},
            status=status.HTTP_403_FORBIDDEN
        )

    logo = request.FILES.get("logo")

    if not logo:
        return Response(
            {"err": "No logo provided."},
            status=status.HTTP_400_BAD_REQUEST
        )

    startup.logo = logo
    startup.save()

    serializer = StartupSerializer(startup)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )
#startup update and delete only founders can do

@api_view(["GET", "PUT", "PATCH", "DELETE"])
def startup_detail(request, startup_id):

    startup = get_object_or_404(
        Startup,
        id=startup_id
    )

    # GET ONE STARTUP
    if request.method == "GET":

        serializer = StartupSerializer(startup)

        return Response(serializer.data)

    # Only founder who owns startup can modify it
    if startup.founder != request.user:

        return Response(
            {"err": "You do not have permission to modify this startup."},
            status=status.HTTP_403_FORBIDDEN
        )

    # UPDATE
    if request.method in ["PUT", "PATCH"]:

        serializer = StartupSerializer(
            startup,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # DELETE
    if request.method == "DELETE":

        startup.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

#startup founder can post role so others can join

@api_view(["POST"])
def role_create(request, startup_id):

    startup = get_object_or_404(
        Startup,
        id=startup_id
    )

    if startup.founder != request.user:

        return Response(
            {"err": "Only the startup founder can create roles."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = StartUpRoleSerializer(
        data=request.data
    )
    if serializer.is_valid():

        serializer.save(
            startup=startup
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

# statup owner can get the roles edit and update them and also delete them

@api_view(["GET", "PUT", "PATCH", "DELETE"])
def role_detail(request, role_id):

    role = get_object_or_404(
        StartUpRole,
        id=role_id
    )

    # Anyone authenticated can view the role
    if request.method == "GET":

        serializer = StartUpRoleSerializer(role)

        return Response(serializer.data)


    # Only the founder who owns the startup
    # can edit or delete this role
    if role.startup.founder != request.user:

        return Response(
            {"err": "Only the startup founder can modify this role."},
            status=status.HTTP_403_FORBIDDEN
        )


    # Update the role
    if request.method in ["PUT", "PATCH"]:

        serializer = StartUpRoleSerializer(
            role,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


    # Delete the role
    if request.method == "DELETE":

        role.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


    
# Users applies to startup


@api_view(["POST"])
def application_create(request, role_id):

    role = get_object_or_404(
        StartUpRole,
        id=role_id
    )

    if not role.is_open:
        return Response(
            {"err": "This role is no longer accepting applications."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.user.profile.user_type != "User":
        return Response(
            {"err": "Only users can apply for startup roles."},
            status=status.HTTP_403_FORBIDDEN
        )

    if Application.objects.filter(
        applicant=request.user,
        role=role
    ).exists():

        return Response(
            {"err": "You have already applied for this role."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ApplicationSerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save(
            applicant=request.user,
            role=role
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

#user can view GET the applications they applied to

@api_view(["GET"])
def my_applications(request):

    applications = Application.objects.filter(
        applicant=request.user
    )

    serializer = ApplicationSerializer(
        applications,
        many=True
    )

    return Response(serializer.data)

#users can get their applications and withdraw from it 

@api_view(["GET", "DELETE"])
def application_detail(request, application_id):

    application = get_object_or_404(
        Application, 
        id = application_id
    )

    # Applicant or startup founder can view

    if (

        application.applicant != request.user
        and application.role.startup.founder != request.user

    ):
        return Response(

            {"err": "You do not have permission to view this application."},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == "GET":

        serializer = ApplicationSerializer(application)

        return Response(serializer.data)
    
    #only applicant can withdraw from their application 

    if request.method == "DELETE":

        if application.applicant != request.user:

            return Response(
                {"err": "Only the applicant can withdraw this application."},
                status=status.HTTP_403_FORBIDDEN
        )

    # If they had already been accepted,
    # also remove them from the startup team

        if application.status == "Accepted":

         TeamMember.objects.filter(
                startup=application.role.startup,
                user=request.user
            ).delete()
        
         application.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

        
#founders can see applicants 

@api_view(["GET"])
def role_applications(request, role_id):

    role = get_object_or_404(
        StartUpRole,
        id=role_id
    )

    if role.startup.founder != request.user:

        return Response(
            {"err": "Only the startup founder can view these applications."},
            status=status.HTTP_403_FORBIDDEN
        )

    applications = Application.objects.filter(
        role=role
    )

    serializer = ApplicationSerializer(
        applications,
        many=True
    )

    return Response(serializer.data)

# application rejection and acceptance

@api_view(["PATCH"])
def application_decision(request, application_id):

    application = get_object_or_404(
        Application,
        id=application_id
    )

    # Only the founder who owns this startup can
    # accept or reject applications
    if application.role.startup.founder != request.user:
        return Response(
            {
                "err": "Only the startup founder can accept or reject this application."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    decision = request.data.get("status")

    # Only these two decisions are allowed
    if decision not in ["Accepted", "Rejected"]:
        return Response(
            {
                "err": "Status must be Accepted or Rejected."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():

        application.status = decision
        application.save()

        team_member = None

        # ACCEPT
        if decision == "Accepted":

            team_member, created = TeamMember.objects.get_or_create(
                startup=application.role.startup,
                user=application.applicant,
                defaults={
                    "role": application.role.title
                }
            )

        # REJECT
        elif decision == "Rejected":

            TeamMember.objects.filter(
                startup=application.role.startup,
                user=application.applicant
            ).delete()

    application_serializer = ApplicationSerializer(application)

    response_data = {
        "application": application_serializer.data
    }

    if team_member:
        team_member_serializer = TeamMemberSerializer(team_member)

        response_data["team_member"] = team_member_serializer.data

    return Response(
        response_data,
        status=status.HTTP_200_OK
    )

# with transaction.atomic(): django creates everything inside it as one operation 

#Get Team members  my team members 

@api_view(["GET"])
def my_team_memberships(request):

    memberships = TeamMember.objects.filter(
        user=request.user
    )

    serializer = TeamMemberSerializer(
        memberships,
        many=True
    )

    return Response(serializer.data)

#founder can remove team members

@api_view(["DELETE"])
def team_member_delete(request, member_id):

    member = get_object_or_404(
        TeamMember,
        id=member_id
    )

    if member.startup.founder != request.user:
        return Response(
            {"err": "Only the startup founder can remove team members."},
            status=status.HTTP_403_FORBIDDEN
        )

    member.delete()

    return Response(
        status=status.HTTP_204_NO_CONTENT
    )

