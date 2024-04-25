from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


class UserProfile(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    otp = models.CharField(max_length=6, blank=True)
    otp_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True,null=True)
    address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15,blank=True)
    branch = models.CharField(max_length=100)
    email_errors = {
        "required": "Email is required",
        "invalid": "Enter a valid email without spaces",
    }

    _email_regex_validator = RegexValidator(
        regex=r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$",
        message="Email must be valid",
    )

    email = models.EmailField(
        "Email",
        unique=True,
        validators=[_email_regex_validator],
        error_messages=email_errors,
    )

    def validate_password(value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r'[A-Z]', value):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*]', value):
            raise ValidationError("Password must contain at least one symbol !@#$%^&*.")


    password = models.CharField(
        "Password",
        max_length=128,
        validators=[validate_password],
        help_text="Your password must contain at least 8 characters, including at least one uppercase letter, one lowercase letter, one digit, and one symbol (!@#$%^&*()-_=+`~[]{};:'\"|,.<>?/).",
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}"
    

