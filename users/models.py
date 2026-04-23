from django.db import models
from django.contrib.auth.models import AbstractUser


# ✅ DEFINE FIRST
ROLE_CHOICES = [
    ('author', 'Author'),
    ('reviewer', 'Reviewer'),
    ('editor', 'Editor'),
]


class User(AbstractUser):
    # ✅ THEN USE IT
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='author'
    )

    def __str__(self):
        return self.username