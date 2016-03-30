from django.db import models


class HendersonPark(models.Model):
    """
    Scraped with permission from Henderson Parks and Rec Website
    """
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=150)
    url = models.URLField()
    img_url = models.URLField(null=True, blank=True, max_length=350)
    created_on = models.DateTimeField(auto_now_add=True)
    modifided_at = models.DateTimeField(auto_now=True)

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