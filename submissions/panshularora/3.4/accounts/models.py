from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('agent',      'Agent'),
        ('supervisor', 'Supervisor'),
        ('admin',      'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='agent')

    def is_supervisor_or_above(self):
        return self.role in ('supervisor', 'admin')

    def __str__(self):
        return f"{self.username} ({self.role})"
