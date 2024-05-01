from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(AbstractUser):
    is_approved = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True)
    otp_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(max_length=20,choices=GENDER_CHOICES)
    occupation = models.CharField(max_length=50)
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
    

#-----------------------------Budgeting and Expense Tracking----------------------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)

class Budget(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    total_budget = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=10, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')])

    def __str__(self):
        return self.category

#-------------------------------------Savings Goals:-------------------------------------------------------------

class Goal(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deadline = models.DateField()


@receiver(post_save, sender=Goal)
def milestone_reached_notification(sender, instance, created, **kwargs):
    if instance.current_amount >= instance.target_amount:
        send_email_notification(instance.user.email, instance.name)

def send_email_notification(user_email, goal_name):
    subject = 'Congratulations! You Reached Your Savings Goal'
    message = f'Congratulations! You have successfully reached your savings goal for {goal_name}.'
    send_mail(subject, message, 'your_email@example.com', [user_email])