from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(

        max_length=11,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^09\d{9}$',
                message='شماره موبایل باید به فرم 09123456789 باشد.',
            )
        ],
    )
    def __str__(self):
        return self.username

