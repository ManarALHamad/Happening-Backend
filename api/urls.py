
# Application programming endpoints (defines the api endpoint)

from django.urls import path
from . import views


urlpatterns = [

    path("auth/sign-up", views.sign_up, name="sign-up"),
    path("auth/sign-in", views.sign_in, name="sign-in"),
    path("users", views.user_list, name="user-list"),
    path("profile", views.profile_detail, name="profile-detail"), #profile
    path("startups", views.startup_list_create, name="startup-list-create"), #create startup
    path("startups/<int:startup_id>", views.startup_detail,name="startup-detail"), #startup details
    path("startups/<int:startup_id>/roles", views.role_create, name="role-create"), #startup roles
    path("roles/<int:role_id>", views.role_detail,name="role-detail"), #startup role details
    path( "roles/<int:role_id>/apply", views.application_create,name="application-create"), #application creation
    path("applications/mine", views.my_applications,name="my-applications"), #view my applications
    path("applications/<int:application_id>", views.application_detail,name="application-detail"),
    path("roles/<int:role_id>/applications", views.role_applications,  name="role-applications" ),  #founder sees applicants
    path("applications/<int:application_id>/decision", views.application_decision, name="application-decision"), #team member accept and reject
    path("team-members/mine", views.my_team_memberships, name="my-team-memberships"), #get my team members 
    path( "team-members/<int:member_id>", views.team_member_delete, name="team-member-delete") #delete team member

]

