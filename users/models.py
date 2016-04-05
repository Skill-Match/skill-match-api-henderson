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


class Skill(models.Model):
    player = models.ForeignKey(User)
    sport = models.CharField(max_length=40)
    skill = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    sportsmanship = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    punctuality = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    num_feedbacks = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return "{}'s {} skill: {}".format(self.player.username, self.sport,
                                          self.skill)

    def calculate(self):
        """
        All feedbacks for a certain sport are tallied to calculate the
        skill and sportsmanship.
        Skills are calculated based on the reviewers credibility. The reviewer's
        skill, sportsmanship, and xp (num_feedbacks) influence how much their
        feedback will be weighted.
        :return:
        """
        # Get all feedbacks for this user in one sport
        feedbacks = Feedback.objects.filter(match__sport=self.sport).\
            filter(player=self.player)

        # Set variables to add to in order to get total
        skill_total = 0
        sportsmanship_total = 0
        total_weight = 0
        count = 0

        for feedback in feedbacks:

            # Get reviewers credibility in this sport+-
            reviewer_cred = feedback.reviewer.skill_set.filter(sport=self.sport)

            # Not sure why the if, else, won't work, because can have xp
            # without sportsmanship or skill...???
            if reviewer_cred:
                reviewer_cred = reviewer_cred[0]
                xp = reviewer_cred.num_feedbacks
                if not xp:
                    xp = 0
                sportsmanship = reviewer_cred.sportsmanship
                if not sportsmanship:
                    sportsmanship = 40
                skill = reviewer_cred.skill
                if not skill:
                    skill = 40
            else:
                # Default values for users with no credibility
                xp = 0
                sportsmanship = 40
                skill = 40

            # Calculate weight based on reviewer credibility
            # i.e. xp = 7, weight = 3...
            if 0 <= xp <= 10:
                weight = 3
            elif 11 < xp < 20:
                weight = 5
            elif 21 < xp < 30:
                weight = 7
            elif 31 < 40:
                weight = 8
            elif 41 < 50:
                weight = 9
            else:
                weight = 10

            # Weight for sportsmanship and skill are heavier than xp. Thus * 2
            # This breaks down to 40% skill, 40% sportsmanship, 20% xp
            # i.e. sportsmanship = 90, weight = 18 (+3 from xp), weight = 21
            weight += int((sportsmanship * 2) / 10)
            # i.e. skill = 75, weight = 15 (+21), weight = 36
            weight += int((skill * 2) / 10)

            # Keep adding the weight to total_weight each iteration
            total_weight += weight

            # i.e. feedback.skill = 50 * 38, skill_total = 1900
            skill_total += (feedback.skill * weight)
            # i.e. feedback.sportsmanship = 90 * 38, sportsmanship_total = 3420
            sportsmanship_total += (feedback.sportsmanship * weight)
            # Count number of feedbacks
            count += 1

        # Get total of all skills and total weight and calculate
        # based on weights
        self.skill = round((skill_total / total_weight), 2)
        self.sportsmanship = round((sportsmanship_total / total_weight), 2)
        self.num_feedbacks = count
        self.save()
