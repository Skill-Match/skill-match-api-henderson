from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


###############################################################################
#
# SPORT CHOICES AND IMAGES FOR USE WITH MULTIPLE MODELS
#
###############################################################################

# SPORT CHOICES for use with multiple models
TENNIS = 'Tennis'
BASKETBALL = 'Basketball'
FOOTBALL = 'Football'
SOCCER = 'Soccer'
VOLLEYBALL = 'Volleyball'
PICKLEBALL = 'Pickleball'
OTHER = 'Other'
SPORT_CHOICES = (
    (TENNIS, 'Tennis'),
    (BASKETBALL, 'Basketball'),
    (FOOTBALL, 'Football'),
    (SOCCER, 'Soccer'),
    (VOLLEYBALL, 'Volleyball'),
    (PICKLEBALL, 'Pickleball'),
    (OTHER, 'Other')
)

TENNIS_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                 "c_scale,w_200/v1451803727/1451824644_tennis_jegpea.png"
BASKETBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451811954/basketball_lxzgmw.png"
FOOTBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                   "c_scale,w_200/v1451812093/American-Football_vbp5ww.png"
SOCCER_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                 "c_scale,w_200/v1451803724/1451824570_soccer_mwvtwy.png"
VOLLEYBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451803790/1451824851_" \
                     "volleyball_v2pu0m.png"
PICKLEBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451803795/1451824990_" \
                     "table_tennis_uqv436.png"
TROPHY_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                "v1451804013/trophy_200_cnaras.jpg"

###############################################################################
#
# PARK RELATED MODELS
#
###############################################################################


class HendersonPark(models.Model):
    """
    Scraped with permission from Henderson Parks and Rec Website
    """
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=150)
    url = models.URLField()
    img_url = models.URLField(null=True, blank=True, max_length=350)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Amenity(models.Model):
    """
    Also scraped from Henderson Parks and Rec.
    ManyToMany Relationship with HendersonPark
    Example amenities: 'Open Grass Field', 'Lighted Tennis Courts'
    Yes I spelled Amenity wrong.
    """
    name = models.CharField(max_length=125)
    parks = models.ManyToManyField(HendersonPark)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Court(models.Model):
    park = models.ForeignKey(HendersonPark, null=True, blank=True)
    sport = models.CharField(max_length=25, choices=SPORT_CHOICES)
    other = models.CharField(max_length=25, null=True, blank=True)
    img_url = models.URLField(default=TROPHY_IMG_URL)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} at {}".format(self.sport, self.park.name)


# After Court object is created, add corresponding sport image.
@receiver(post_save, sender=Court)
def add_profile_image(sender, instance=None, created=False, **kwargs):

    if created:
        if instance.sport == 'Tennis':
            instance.img_url = TENNIS_IMG_URL
        elif instance.sport == 'Basketball':
            instance.img_url = BASKETBALL_IMG_URL
        elif instance.sport == 'Football':
            instance.img_url = FOOTBALL_IMG_URL
        elif instance.sport == 'Soccer':
            instance.img_url = SOCCER_IMG_URL
        elif instance.sport == 'Volleyball':
            instance.img_url = VOLLEYBALL_IMG_URL
        elif instance.sport == 'Pickleball':
            instance.img_url = PICKLEBALL_IMG_URL

        instance.save()
