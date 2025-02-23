from django.db import models
from django.contrib.auth.models import User


class MyPermissionsModel(models.Model):
    # Example model fields
    name = models.CharField(max_length=100)

    class Meta:
        permissions = (
            ("custom_permission", "Team Planning owner"),
        )

