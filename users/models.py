from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def create_user_token(sender, instance=None, created=False, **kwargs):
    # When User object is created, Token with 1to1 is created for that user.
    if created:
        Token.objects.create(user=instance)


class Profile(models.Model):
    MALE = 'Male'
    FEMALE = 'Female'
    OTHER = 'Other'
    UNDER_18 = 'Under 18'
    LATE_TEEN = '18-19'
    TWENTIES = "20's"
    THIRTIES = "30's"
    FORTIES = "40's"
    FIFTIES = "50's"
    SIXTY = "60+"

    GENDER_CHOICES = (
        (MALE, 'Man'),
        (FEMALE, 'Woman'),
        (OTHER, 'Other')
    )
    AGE_CHOICES = (
        (UNDER_18, 'Under 18'),
        (LATE_TEEN, '18-19'),
        (TWENTIES, "20's"),
        (THIRTIES, "30's"),
        (FORTIES, "40's"),
        (FIFTIES, "50's"),
        (SIXTY, "60+")
    )

    user = models.OneToOneField(User)
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES,
                              default=MALE)
    age = models.CharField(max_length=8, choices=AGE_CHOICES, default=TWENTIES)
    wants_texts = models.BooleanField(default=False)
    phone_number = models.CharField(null=True, blank=True, max_length=15)
