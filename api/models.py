from django.db import models
from django.contrib.auth.models import User

# Create your Profile

class Profile(models.Model):

    USER_TYPE_CHOICES = [

        ("Founder", "Founder"),
        ("User", "User"),
    ]

    EXPERIENCE_LEVEL_CHOICES = [

        ("Student", "Student"),
        ("Junior", "Junior"),
        ("Mid-Level", "Mid-Level"),
        ("Senior", "Senior"),
        ("Founder", "Founder"),
        
    ]

    user = models.OneToOneField(

        User,
        on_delete=models.CASCADE,
        related_name="profile"

    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="User"
    )

    bio = models.TextField(blank=True)

    location = models.CharField(
        max_length=100,
        blank=True,
        default="Bahrain"
    )

    skills = models.TextField(
        blank=True,
        help_text="Comma separated skills"
    )

    experience_level = models.CharField(

        max_length=20,
        choices=EXPERIENCE_LEVEL_CHOICES,
        blank=True
    )

    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    profile_image = models.ImageField(

        upload_to="profiles/",
        blank=True,
        null=True

    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

# Create your StartUp

class Startup(models.Model):

    STAGE_CHOICES =[

        ("Idea", "Idea"),
        ("Building", "Building"),
        ("MVP", "MVP"),
        ("Launched", "Launched"),
        ("Growing", "Growing"),
    ]

    INDUSTRY_CHOICES = [

        ("Technology", "Technology"),
        ("AI", "AI"),
        ("FinTech", "FinTech"),
        ("HealthTech", "HealthTech"),
        ("EdTech", "EdTech"),
        ("E-Commerce", "E-Commerce"),
        ("SaaS", "SaaS"),
        ("Food", "Food"),
        ("Fashion", "Fashion"),
        ("Other", "Other"),

    ]

    founder = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="startups"
    )

    description =models.TextField()

    problem = models.TextField(
        blank=True
    )

    solution= models.TextField(
        blank=True
    )

    industry = models.CharField(
        max_length=50,
        choices=INDUSTRY_CHOICES,
        default="Technology"
    )

    stage = models.CharField(
        max_length=20,
        choices=STAGE_CHOICES,
        default="Idea"
    )

    location = models.CharField(
        max_length=100,
        default="Bahrain"
    )

    website = models.URLField(
        blank=True
    )

    logo = models.ImageField(
        upload_to="startup_logos/",
        blank=True,
        null=True
    )

    is_recruiting = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


#StartUp role jobs/ team members the founder is seeking

class StartUpRole(models.Model):

    ROLE_TYPE_CHOICES = [

        ("Co-Founder", "Co-Founder"),
        ("Developer", "Developer"),
        ("Designer", "Designer"),
        ("Marketing", "Marketing"),
        ("Business", "Business"),
        ("Sales", "Sales"),
        ("Data", "Data"),
        ("AI", "AI"),
        ("Other", "Other"),

    ]

    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name="roles"
    )

    title = models.CharField(
        max_length=100
    )

    role_type = models.CharField(
        max_length=50,
        choices=ROLE_TYPE_CHOICES
    )

    description = models.TextField()

    required_skills = models.TextField(
        blank=True,
        help_text="Comma separated skills"
    )

    is_open = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.startup.name} - {self.title}"


#Startup applications that user can apply to 

class Application(models.Model):

    STATUS_CHOICES = (

        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    )

    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    role = models.ForeignKey(

        StartUpRole,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    message = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"

    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    #it prevents a single applicant from applying to the same role more than once in the db

    class Meta:
        ordering = ["-created_at"]

        constraints =[
            models.UniqueConstraint(
                fields=["applicant", "role"],
                name="unique_application_per_role"

            )

        ]
    def __str__(self):
        return f"{self.applicant.username} → {self.role.title}"


# StartUp team members 

class TeamMember(models.Model):

    startup = models.ForeignKey(
        Startup,
        on_delete=models.CASCADE,
        related_name="team_members"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="startup_memberships"
    )

    role = models.CharField(
        max_length=100
    )

    joined_at = models.DateTimeField(
        auto_now_add=True
    )

# prevents duplicate records in a database table.

class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["startup", "user"],
            name="unique_startup_team_member"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.startup.name}"









