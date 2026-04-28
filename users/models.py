from django.db import models
from django.contrib.auth.models import AbstractUser


# ✅ DEFINE FIRST
ROLE_CHOICES = [
    ('author', 'Author'),
    ('reviewer', 'Reviewer'),
    ('editor', 'Editor'),
    ('editor-in-chief', 'Editor-in-Chief'),
    ('managing-editor', 'Managing Editor'),
    ('associate-editor', 'Associate Editor'),
    ('editorial-assistant', 'Editorial Assistant'),
]


class User(AbstractUser):
    # ✅ THEN USE IT
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='author'
    )

    institute_name = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    designation = models.CharField(max_length=255, blank=True)
    expertise_area = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.username